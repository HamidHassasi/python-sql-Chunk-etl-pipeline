/* SQL Server / T-SQL. Run in the target database. */
IF SCHEMA_ID(N'stg') IS NULL EXEC(N'CREATE SCHEMA stg');
IF SCHEMA_ID(N'dw') IS NULL EXEC(N'CREATE SCHEMA dw');
GO
IF OBJECT_ID(N'stg.sales_load',N'U') IS NULL
CREATE TABLE stg.sales_load (
 sales_id varchar(32) NOT NULL, transaction_date date NOT NULL, customer_id varchar(32) NOT NULL,
 store_id varchar(16) NOT NULL, product_code varchar(32) NOT NULL, quantity int NOT NULL,
 unit_price decimal(12,2) NOT NULL, discount decimal(5,4) NOT NULL,
 payment_status varchar(16) NOT NULL, city nvarchar(100) NOT NULL,
 load_id uniqueidentifier NOT NULL CONSTRAINT DF_sales_load_load_id DEFAULT NEWID(),
 loaded_at datetime2(0) NOT NULL CONSTRAINT DF_sales_load_loaded_at DEFAULT SYSUTCDATETIME(),
 CONSTRAINT CK_sales_qty CHECK(quantity>0), CONSTRAINT CK_sales_price CHECK(unit_price>=0),
 CONSTRAINT CK_sales_discount CHECK(discount>=0 AND discount<=1));
GO
IF OBJECT_ID(N'dw.fact_sales',N'U') IS NULL
CREATE TABLE dw.fact_sales (
 sales_id varchar(32) NOT NULL CONSTRAINT PK_fact_sales PRIMARY KEY,
 transaction_date date NOT NULL, customer_id varchar(32) NOT NULL, store_id varchar(16) NOT NULL,
 product_code varchar(32) NOT NULL, quantity int NOT NULL, unit_price decimal(12,2) NOT NULL,
 discount decimal(5,4) NOT NULL, payment_status varchar(16) NOT NULL, city nvarchar(100) NOT NULL,
 net_amount AS CONVERT(decimal(18,2),quantity*unit_price*(1-discount)) PERSISTED,
 loaded_at datetime2(0) NOT NULL CONSTRAINT DF_fact_sales_loaded_at DEFAULT SYSUTCDATETIME());
GO
/* Query-oriented indexes: date/status reporting and customer history. */
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'IX_fact_sales_date_status' AND object_id=OBJECT_ID(N'dw.fact_sales'))
 CREATE INDEX IX_fact_sales_date_status ON dw.fact_sales(transaction_date,payment_status) INCLUDE(quantity,unit_price,discount,city,product_code);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'IX_fact_sales_customer_date' AND object_id=OBJECT_ID(N'dw.fact_sales'))
 CREATE INDEX IX_fact_sales_customer_date ON dw.fact_sales(customer_id,transaction_date) INCLUDE(net_amount,store_id);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'IX_sales_load_loadid' AND object_id=OBJECT_ID(N'stg.sales_load'))
 CREATE INDEX IX_sales_load_loadid ON stg.sales_load(load_id) INCLUDE(sales_id,transaction_date);
GO
