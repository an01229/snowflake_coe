from sqlalchemy import create_engine
import urllib
import pandas as pd

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=sf-coe-sql-server.database.windows.net;"
    "DATABASE=coe-dev-db;"
    "UID=saikrishna_c;"
    "PWD=SaiPassword#2025;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")
df.head(10000).to_sql("online_payment_fraud_detection", con=engine, if_exists='replace', index=False, chunksize=1000)
