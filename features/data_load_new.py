import pandas as pd
import urllib
from sqlalchemy import create_engine
import numpy as np

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

# Load the CSV
df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")

# OPTIONAL: Clean/cast columns to prevent dtype issues
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["step"] = pd.to_numeric(df["step"], errors="coerce")
df["isFraud"] = pd.to_numeric(df["isFraud"], errors="coerce")
df["isFlaggedFraud"] = pd.to_numeric(df["isFlaggedFraud"], errors="coerce")

# Break into chunks
chunk_size = 10000
chunks = np.array_split(df, int(len(df) / chunk_size) + 1)

for i, chunk in enumerate(chunks):
    try:
        print(f"Uploading chunk {i+1}/{len(chunks)}... rows: {len(chunk)}")
        chunk.to_sql(
            name="online_payment_fraud_detection",
            con=engine,
            if_exists="append" if i > 0 else "replace",
            index=False,
            chunksize=1000  # batch within each chunk
        )
        print(f"✅ Chunk {i+1} uploaded successfully.")
    except Exception as e:
        print(f"❌ Failed on chunk {i+1}: {e}")
        break
