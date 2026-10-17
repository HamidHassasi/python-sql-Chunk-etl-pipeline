#!/usr/bin/env python3
"""Generate reproducible synthetic retail sales data."""
import argparse, csv, random
from datetime import date, timedelta
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--output',default=str(Path(__file__).with_name('sample_large_sales.csv'))); p.add_argument('--rows',type=int,default=10000); p.add_argument('--seed',type=int,default=42); a=p.parse_args()
 if a.rows<1: p.error('--rows must be positive')
 rng=random.Random(a.seed); start=date(2023,1,1); cities=['Tehran','Shiraz','Isfahan','Tabriz','Mashhad','Karaj','Yazd','Rasht','Ahvaz','Kerman']; products=[f'PRD-{i:04d}' for i in range(1,121)]
 out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f); w.writerow(['sales_id','transaction_date','customer_id','store_id','product_code','quantity','unit_price','discount','payment_status','city'])
  for i in range(1,a.rows+1):
   dt=start+timedelta(days=rng.randrange(730)); w.writerow([f'S{dt:%y%m}-{i:07d}',dt.isoformat(),f'C{rng.randint(1,2500):06d}',f'ST{rng.randint(1,45):03d}',rng.choice(products),rng.randint(1,12),f'{rng.uniform(2,1500):.2f}',f'{rng.choice([0,.05,.1,.15,.2]):.2f}',rng.choices(['PAID','PENDING','REFUNDED','FAILED'],[.78,.12,.06,.04])[0],rng.choice(cities)])
 print(f'Generated {a.rows:,} rows: {out.resolve()}')
if __name__=='__main__': main()
