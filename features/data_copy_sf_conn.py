from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, upper, when
import pandas as pd
import pyodbc

# Establishing connection to SQL Server
try:
    sql_conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=sf-coe-sql-server.database.windows.net,1433;'
        'DATABASE=coe-dev-db;'
        'UID=saikrishna_c;'
        'PWD=SaiPassword#2025;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=60;'
    )
    print("✅ Connected to SQL Server.")
except Exception as e:
    print("❌ SQL Server connection failed:", e)
    exit()

# Fetching data from SQL Server
try:
    df = pd.read_sql("SELECT * FROM online_payment_fraud_detection", sql_conn)
    print(f"✅ Retrieved {len(df)} records from SQL Server.")
    sql_conn.close()
except Exception as e:
    print("❌ Failed to fetch data from SQL Server:", e)
    exit()


snowflake_config = {
    "account": "anblickspartner.anblicksorg.azure",          # e.g., "xy12345.us-east-1"
    "user": "saikrishna.c",
    "password": "SaiPassword#2025",
    "role": "COE_DEV_ROLE",
    "warehouse": "ANBLICKS_H2S_WH",
    "database": "COE_DATABASE",
    "schema": "COE_POC_SCHEMA"
}

#Establishing snowflake session
try:
    session = Session.builder.configs(snowflake_config).create()
    print("✅ Connected to Snowflake.")
except Exception as e:
    print("❌ Snowflake connection failed:", e)
    exit()

# Write data ti snowflake staging table
try:
    session.write_pandas(
        df=df,
        table_name="online_payment_fraud_staging",
        auto_create_table=True,
        overwrite=True
    )
    print("✅ Data written to staging table.")
except Exception as e:
    print("❌ Failed to write to Snowflake:", e)
    session.close()
    exit()

# Adding transformation columns and writing to final curate table
try:
    sf_df = session.table("online_payment_fraud_staging")

    print("✅ Loaded data from staging table into Snowflake DataFrame.")
    transformed_df = (
        sf_df
        .with_column("AMOUNT_USD", col("AMOUNT") * 1.0)
        .with_column("TYPE_UPPER", upper(col("TYPE")))
        .with_column("IS_HIGH_VALUE", when(col("AMOUNT") > 10000, 1).otherwise(0))
    )

    transformed_df.write.mode("overwrite").save_as_table("online_payment_fraud_final")
    print("✅ Final transformed data written to Snowflake.")

except Exception as e:
    print("❌ Transformation failed:", e)

session.close()
