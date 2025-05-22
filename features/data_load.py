import pandas as pd
import pyodbc

# Load CSV
df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")

# SQL Server connection
sql_conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=sf-coe-sql-server.database.windows.net;'
    'DATABASE=coe-dev-db;'
    'UID=saikrishna_c;'
    'PWD=SaiPassword#2025'
)

cursor = sql_conn.cursor()

# Optional: Create table (adjust columns to match your CSV)
cursor.execute("""
CREATE TABLE online_payment_fraud_detection (
    step INT,
    type VARCHAR(100),
    amount DECIMAL(10, 2),
    nameOrig VARCHAR(100),
    oldbalanceOrg DECIMAL(10, 2),
    newbalanceOrig DECIMAL(10, 2),
    nameDest VARCHAR(100),
    oldbalanceDest DECIMAL(10, 2),
    newbalanceDest DECIMAL(10, 2),
    isFraud INT,
    isFlaggedFraud INT
)
""")
sql_conn.commit()

# Insert data
for index, row in df.iterrows():
    cursor.execute(
        "INSERT INTO your_table (step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        row['step'], row['type'], row['amount'], row['nameOrig'],
        row['oldbalanceOrg'], row['newbalanceOrig'], row['nameDest'],
        row['oldbalanceDest'], row['newbalanceDest'],
        row['isFraud'], row['isFlaggedFraud']
    )
sql_conn.commit()

cursor.close()
sql_conn.close()