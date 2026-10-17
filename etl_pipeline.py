#!/usr/bin/env python3
"""Chunked CSV-to-SQL Server ETL. Idempotent inserts keyed by sales_id."""
import argparse, json, logging, sys, time
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

COLS=['sales_id','transaction_date','customer_id','store_id','product_code','quantity','unit_price','discount','payment_status','city']
LOG=logging.getLogger('bi_etl')
def setup(log_file=None):
 h=[logging.StreamHandler(sys.stderr)]
 if log_file: h.append(logging.FileHandler(log_file,encoding='utf-8'))
 logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=h,force=True)
def validate(df, line):
 missing=set(COLS)-set(df.columns)
 if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
 if df[COLS].isnull().any().any(): raise ValueError(f'Null required value near CSV row {line}')
 df=df[COLS].copy(); df['transaction_date']=pd.to_datetime(df.transaction_date,errors='coerce').dt.date
 for c in ['quantity','unit_price','discount']: df[c]=pd.to_numeric(df[c],errors='coerce')
 if df.isnull().any().any(): raise ValueError(f'Invalid typed value near CSV row {line}')
 if (df.quantity<=0).any() or (df.unit_price<0).any() or ((df.discount<0)|(df.discount>1)).any(): raise ValueError(f'Business rule violation near CSV row {line}')
 if df.sales_id.duplicated().any(): raise ValueError(f'Duplicate sales_id within batch near CSV row {line}')
 return df

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--input',required=True); p.add_argument('--batch-size',type=int,default=5000); p.add_argument('--db-conn',required=True,help='SQLAlchemy connection URL, e.g. mssql+pyodbc://...'); p.add_argument('--log-file'); p.add_argument('--schema',default='stg'); p.add_argument('--table',default='sales_load'); a=p.parse_args(); setup(a.log_file)
 if a.batch_size<1: p.error('--batch-size must be positive')
 path=Path(a.input)
 if not path.is_file(): raise FileNotFoundError(f'Input file not found: {path}')
 if not a.schema.replace('_','').isalnum() or not a.table.replace('_','').isalnum(): raise ValueError('Invalid destination identifier')
 connect_args={}; execution_options={}
 if 'mssql' in a.db_conn:
  connect_args={'fast_executemany':True}  # pyodbc fast_executemany only for mssql
 engine=create_engine(a.db_conn,pool_pre_ping=True,connect_args=connect_args); total=0; started=time.time()
 q1,q2=engine.dialect.identifier_preparer.quote(a.schema),engine.dialect.identifier_preparer.quote(a.table)
 hint=' WITH (UPDLOCK,HOLDLOCK)' if engine.dialect.name=='mssql' else ''
 insert=text(f"INSERT INTO {q1}.{q2} (sales_id,transaction_date,customer_id,store_id,product_code,quantity,unit_price,discount,payment_status,city) SELECT :sales_id,:transaction_date,:customer_id,:store_id,:product_code,:quantity,:unit_price,:discount,:payment_status,:city WHERE NOT EXISTS (SELECT 1 FROM {q1}.{q2}{hint} WHERE sales_id=:sales_id)")
 try:
  for n,chunk in enumerate(pd.read_csv(path,chunksize=a.batch_size,dtype={'sales_id':'string','customer_id':'string','store_id':'string','product_code':'string','payment_status':'string','city':'string'}),1):
   frame=validate(chunk,(n-1)*a.batch_size+2); records=frame.to_dict('records')
   with engine.begin() as con: con.execute(insert,records)
   total+=len(records); LOG.info('Validated and processed chunk=%d rows=%d',n,len(records))
  print(json.dumps({'status':'success','rows_processed':total,'elapsed_seconds':round(time.time()-started,2)}))
 finally: engine.dispose()

if __name__=='__main__':
 try: main(); sys.exit(0)
 except Exception as exc:
  logging.getLogger('bi_etl').exception('ETL failed: %s',exc); sys.exit(1)
