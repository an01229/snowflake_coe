from sqlalchemy import create_engine
import urllib
import pandas as pd

# Connection string
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

# Load entire CSV
df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")

#Ingesting the data in chunks into SQL Server object
df.to_sql(
    name="online_payment_fraud_detection",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=5000
)

print(f"Successfully inserted {len(df)} records.")
