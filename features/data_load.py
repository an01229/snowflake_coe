import pandas as pd
import pyodbc

# Load CSV
df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")


connection_string = (
    'Driver={ODBC Driver 18 for SQL Server};'
    'Server=tcp:sf-coe-sql-server.database.windows.net,1433;'
    'Database=coe-dev-db;'
    'Uid=saikrishna_c;'
    'Pwd=SaiPassword#2025;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=60;'
    #'Authentication=ActiveDirectoryPassword'
)

try:
    print("Connecting to the database...")
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
    cursor = conn.cursor()

    # Example query
    cursor.execute("SELECT name FROM sys.databases;")
    for row in cursor.fetchall():
        print(row)
    
    # Close the connection
    conn.close()

except Exception as e:
    print("Connection failed:", e)

# Optional: Create table (adjust columns to match your CSV)
# cursor.execute("""
# -- Drop the table if it exists
# IF OBJECT_ID('online_payment_fraud_detection', 'U') IS NOT NULL
#     DROP TABLE online_payment_fraud_detection;
# -- Create the table with appropriate data types
# -- Adjust the data types based on your CSV file
# CREATE TABLE online_payment_fraud_detection (
#     step INT,
#     type VARCHAR(100),
#     amount DECIMAL(10, 2),
#     nameOrig VARCHAR(100),
#     oldbalanceOrg DECIMAL(10, 2),
#     newbalanceOrig DECIMAL(10, 2),
#     nameDest VARCHAR(100),
#     oldbalanceDest DECIMAL(10, 2),
#     newbalanceDest DECIMAL(10, 2),
#     isFraud INT,
#     isFlaggedFraud INT
# )
# """)
# sql_conn.commit()

# # Insert data
# for index, row in df.iterrows():
#     cursor.execute(
#         "INSERT INTO online_payment_fraud_detection (step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#         row['step'], row['type'], row['amount'], row['nameOrig'],
#         row['oldbalanceOrg'], row['newbalanceOrig'], row['nameDest'],
#         row['oldbalanceDest'], row['newbalanceDest'],
#         row['isFraud'], row['isFlaggedFraud']
#     )
# sql_conn.commit()

# cursor.close()
# sql_conn.close()

