from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd
import pyodbc

# Step 1: SQL Server Connection
sql_conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=sf-coe-sql-server.database.windows.net,1433;'
    'DATABASE=coe-dev-db;'
    'UID=saikrishna_c;'
    'PWD=SaiPassword#2025;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

# Step 2: Read from SQL Server table into Pandas
df = pd.read_sql("SELECT * FROM your_table", sql_conn)
sql_conn.close()

# Step 3: Snowflake Snowpark Session Config
snowflake_config = {
    "account": "your_account_id",
    "user": "your_user",
    "password": "your_password",
    "role": "your_role",
    "warehouse": "your_warehouse",
    "database": "your_database",
    "schema": "your_schema"
}
session = Session.builder.configs(snowflake_config).create()

# Step 4: Load DataFrame into Snowflake Table
session.write_pandas(
    df=df,
    table_name="your_target_table",
    auto_create_table=True,  # set to False if table already exists
    overwrite=True           # or append=True to keep existing data
)

print("Data loaded into Snowflake successfully.")

session.close()
