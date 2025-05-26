from sqlalchemy import create_engine
import urllib
import pandas as pd

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=sf-coe-sql-server.database.windows.net;"
    "DATABASE=coe-dev-db;"
    "UID=saikrishna_c;"
    "PWD=SaiPassword#2025;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

try:
    df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")

    print(f"Attempting to load {len(df)} records...")

    print(df.dtypes)
    print(df.head())

    # Convert columns to appropriate types
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["step"] = pd.to_numeric(df["step"], errors="coerce")


    df.to_sql(
        name="online_payment_fraud_detection",
        con=engine,
        if_exists="append",  # or "append"
        index=False,
        chunksize=2000
    )

    print("Data load successful.")

except Exception as e:
    print("❌ Error occurred during load:")
    print(e)
