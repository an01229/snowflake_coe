import pandas as pd
import pyodbc

# Load CSV
df = pd.read_csv("/Users/saikrishnareddy/onlinefraud.csv")

# Convert DataFrame to list of tuples for fast insertion
data = list(df.itertuples(index=False, name=None))

# Connection string
connection_string = (
    'Driver={ODBC Driver 18 for SQL Server};'
    'Server=tcp:sf-coe-sql-server.database.windows.net,1433;'
    'Database=coe-dev-db;'
    'Uid=saikrishna_c;'
    'Pwd=SaiPassword#2025;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=60;'
)

try:
    # Connect
    print("Connecting to the database...")
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    IF OBJECT_ID('online_payment_fraud_detection', 'U') IS NOT NULL
        DROP TABLE online_payment_fraud_detection;

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
    conn.commit()

    # Use fast batch insert
    insert_sql = """
    INSERT INTO online_payment_fraud_detection (
        step, type, amount, nameOrig, oldbalanceOrg,
        newbalanceOrig, nameDest, oldbalanceDest,
        newbalanceDest, isFraud, isFlaggedFraud
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    print("Inserting data (this may take a few minutes)...")
    cursor.executemany(insert_sql, data)
    conn.commit()
    print(f"Inserted {len(data)} records successfully!")

    # Close connections
    cursor.close()
    conn.close()

except Exception as e:
    print("Error occurred:", e)
