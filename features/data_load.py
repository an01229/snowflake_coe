import pandas as pd
import pyodbc

# Load the CSV
df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")

#Break data into batches
batch_size = 10000
data_batches = [df.iloc[i:i+batch_size] for i in range(0, len(df), batch_size)]

# Define the connection string
connection_string = (
    'Driver={ODBC Driver 18 for SQL Server};'
    'Server=tcp:sf-coe-sql-server.database.windows.net,1433;'
    'Database=coe-dev-db;'
    'Uid=saikrishna_c;'
    'Pwd=SaiPassword#2025;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=120;'  # increased to 120 seconds
)

try:
    print("Connecting to the database...")
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
    cursor = conn.cursor()

    # Drop & create table
    # cursor.execute("""
    # IF OBJECT_ID('online_payment_fraud_detection', 'U') IS NOT NULL
    #     DROP TABLE online_payment_fraud_detection;

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
    # conn.commit()

    cursor.execute("SELECT TOP 1 name FROM sys.databases")
    print(cursor.fetchone())


    # Insert data in batches
    # insert_sql = """
    # INSERT INTO online_payment_fraud_detection (
    #     step, type, amount, nameOrig, oldbalanceOrg,
    #     newbalanceOrig, nameDest, oldbalanceDest,
    #     newbalanceDest, isFraud, isFlaggedFraud
    # ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    # """

    # for i, batch_df in enumerate(data_batches):
    #     print(f"Inserting batch {i+1}/{len(data_batches)}")
    #     data = list(batch_df.itertuples(index=False, name=None))
    #     cursor.executemany(insert_sql, data)
    #     conn.commit()

    # print("All batches inserted successfully.")

    cursor.close()
    conn.close()

except Exception as e:
    print("Error occurred:", e)
