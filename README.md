# bi-etl-pipeline

**Portfolio project | Business Intelligence • Data Engineering • SQL Server • SSIS**

A reproducible, chunked CSV-to-SQL Server ingestion starter. It demonstrates validation, operational logging, database staging, and orchestration from SSIS. The included 10,000-row synthetic CSV is for demos only—not a real customer dataset.

## Architecture

`CSV source → pandas chunk reader → schema/business validation → SQLAlchemy transaction → stg.sales_load → downstream DW processing → dw.fact_sales → BI/reporting`

`data/raw/generate_sample_data.py` creates deterministic synthetic retail transactions. `etl_pipeline.py` reads bounded batches, validates required fields/types/ranges, and writes to staging. SQL defines staging, warehouse fact, constraints, computed net sales and reporting indexes. SSIS Execute Process Task provides scheduling/orchestration and receives process logs/exit status.

## Tech stack

Python 3.10+, pandas, SQLAlchemy 2, pyodbc / Microsoft ODBC Driver, SQL Server T-SQL, SSIS. The Python ETL loads staging; it does **not** automatically promote rows to the fact table. Implement a controlled stored procedure/SSIS data flow for deduplication, rejection handling and promotion appropriate to your warehouse.

## Quick start (Windows / SQL Server)

1. Install Python and Microsoft ODBC Driver for SQL Server. Create a virtual environment and install dependencies:
   ```powershell
   cd bi-etl-pipeline
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create a SQL Server database, then run `sql/schema.sql` against it using SSMS/sqlcmd.
3. Generate demo CSV (optional; provided file is already included):
   ```powershell
   python data/raw/generate_sample_data.py --rows 10000
   ```
4. Run ETL with a SQLAlchemy URL (example uses Windows trusted auth; URL-encode special characters and driver name as needed):
   ```powershell
   python etl_pipeline.py --input data/raw/sample_large_sales.csv --batch-size 2000 --db-conn "mssql+pyodbc://@localhost/YourDatabase?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
   ```
   For SQL authentication, use a protected secret/configuration source; do not commit credentials. Check SQL Server/driver TLS settings for your environment.

## Chunking, reliability and caveats

`--batch-size` limits pandas' in-memory frame size; tune it to available RAM and database throughput (start at 2,000–10,000). Each chunk is one database transaction, so a failed later chunk does not roll back committed earlier chunks. The SQL insert skips IDs already in staging, allowing a rerun, but the input should have unique IDs and concurrent writers should be coordinated. Invalid/null values and out-of-range quantity, price or discount fail fast. Production extensions should add a rejected-record quarantine, source/load identifiers, metrics/alerts, retry policy, schema evolution, least-privilege credentials and a promotion/merge procedure.

### Benchmarks

No hardware-dependent throughput claim is made: performance varies with SQL Server, ODBC driver, network, indexes and batch size. Measure end-to-end elapsed time and rows/sec in your target environment; compare several batch sizes and record host/DB configuration before publishing benchmark numbers.

## SSIS integration

See [`ssis/SSIS_INTEGRATION_GUIDE.md`](ssis/SSIS_INTEGRATION_GUIDE.md) for Execute Process Task setup, argument quoting, parameters, standard output/error capture, exit codes, variable mapping, secret handling, and deployment checklist. SSIS should mark the task failed for any non-zero process exit code.

## Repository map

```text
bi-etl-pipeline/
├── data/raw/generate_sample_data.py
├── data/raw/sample_large_sales.csv
├── sql/schema.sql
├── ssis/SSIS_INTEGRATION_GUIDE.md
├── etl_pipeline.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Push to GitHub

Create an empty GitHub repository, then from this folder:
```bash
git init
git add README.md .gitignore requirements.txt etl_pipeline.py data sql ssis
git commit -m "Build chunked SQL Server BI ETL pipeline"
git branch -M main
git remote add origin https://github.com/YOUR-USER/bi-etl-pipeline.git
git push -u origin main
```
Review staged files and secrets before pushing. The sample CSV is deliberately unignored; remove it from Git if repository size/policy requires, since the generator can recreate it.

---

# bi-etl-pipeline (فارسی)

**پروژه نمونه‌کار هوش تجاری و مهندسی داده؛ Python، SQL Server و SSIS**

این پروژه نمونه‌ای بازتولیدپذیر برای انتقال CSV به SQL Server است. داده‌ها ساختگی‌اند و اطلاعات مشتری واقعی نیستند.

## معماری

`CSV ← خواندن دسته‌ای با pandas ← اعتبارسنجی ← تراکنش SQLAlchemy ← جدول stg.sales_load ← پردازش انبار داده ← dw.fact_sales ← گزارش‌های BI`

اسکریپت تولید داده، تراکنش‌های فروش نمونه می‌سازد. ETL فایل را دسته‌به‌دسته می‌خواند، ستون‌ها و قواعد را بررسی می‌کند و داده معتبر را در جدول staging می‌نویسد. فایل SQL ساختار staging و fact، محدودیت‌ها، مبلغ خالص محاسباتی و ایندکس‌های گزارش‌گیری را تعریف می‌کند. اجرای زمان‌بندی‌شده می‌تواند از SSIS انجام شود.

## فناوری‌ها و بهینه‌سازی

Python 3.10+، pandas، SQLAlchemy، pyodbc، SQL Server و SSIS. پارامتر `--batch-size` حافظه مصرفی هر دسته را کنترل می‌کند؛ از ۲٬۰۰۰ تا ۱۰٬۰۰۰ شروع کنید و متناسب با RAM، شبکه و دیتابیس تنظیم کنید. هر دسته تراکنش مستقل دارد؛ بنابراین اگر دسته‌ای شکست بخورد، دسته‌های قبلی ممکن است ثبت شده باشند. شناسه‌های موجود در staging دوباره درج نمی‌شوند. ETL فعلی صرفاً staging را پر می‌کند؛ انتقال کنترل‌شده به fact باید با رویه ذخیره‌شده یا Data Flow مناسب پیاده‌سازی شود.

## اجرا

در ویندوز، Python، ODBC Driver و دسترسی SQL Server را آماده کنید؛ سپس محیط مجازی ساخته و `pip install -r requirements.txt` را اجرا کنید. ابتدا `sql/schema.sql` را روی دیتابیس اجرا کنید. برای ساخت داده نمونه:

```powershell
python data/raw/generate_sample_data.py --rows 10000
```

سپس نمونه اجرا:

```powershell
python etl_pipeline.py --input data/raw/sample_large_sales.csv --batch-size 2000 --db-conn "mssql+pyodbc://@localhost/YourDatabase?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
```

اطلاعات ورود را در Git ثبت نکنید؛ در SSIS از متغیرهای محیطی/پارامترهای محافظت‌شده استفاده کنید. راهنمای کامل Execute Process Task، آرگومان‌ها، stdout/stderr، کد خروج و متغیرهای SSIS در `ssis/SSIS_INTEGRATION_GUIDE.md` است. کد خروج صفر موفقیت و کد ۱ خطاست.

## بنچمارک و انتشار

سرعت ثابت و تضمین‌شده اعلام نشده، چون به سخت‌افزار، درایور، شبکه، ایندکس‌ها و اندازه دسته بستگی دارد. در محیط خود چند اندازه دسته را اندازه بگیرید و زمان و تعداد ردیف‌ها را همراه مشخصات محیط ثبت کنید. برای انتشار در GitHub از دستورات بخش انگلیسی README استفاده کنید و پیش از push، فایل‌های staged و نبود رمز عبور را بررسی کنید.
