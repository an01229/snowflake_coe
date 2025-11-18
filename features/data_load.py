import os
import sys
import logging
from typing import Iterator

import pandas as pd
import pyodbc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_connection() -> pyodbc.Connection:
    """
    Establishes SQL Server connection using environment variables.
    
    Returns:
        pyodbc Connection object
    """
    connection_string = (
        f'Driver={{ODBC Driver 18 for SQL Server}};'
        f'Server=tcp:{os.getenv("SQL_SERVER_HOST")};'
        f'Database={os.getenv("SQL_SERVER_DB")};'
        f'Uid={os.getenv("SQL_SERVER_USER")};'
        f'Pwd={os.getenv("SQL_SERVER_PASSWORD")};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
        f'Connection Timeout=120;'
    )
    
    conn = pyodbc.connect(connection_string)
    logger.info("✅ Connected to SQL Server")
    return conn


def read_csv_in_chunks(file_path: str, chunksize: int = 10000) -> Iterator[pd.DataFrame]:
    """
    Reads CSV file in chunks to avoid loading entire file into memory.
    
    Args:
        file_path: Path to CSV file
        chunksize: Number of rows per chunk
        
    Yields:
        DataFrame chunks
    """
    logger.info(f"Reading CSV from {file_path} in chunks of {chunksize}")
    
    for chunk in pd.read_csv(file_path, chunksize=chunksize):
        yield chunk


def create_table_if_not_exists(cursor: pyodbc.Cursor) -> None:
    """
    Creates the target table if it doesn't exist.
    
    Args:
        cursor: Database cursor
    """
    create_table_sql = """
    IF OBJECT_ID('online_payment_fraud_detection', 'U') IS NULL
    BEGIN
        CREATE TABLE online_payment_fraud_detection (
            step INT,
            type VARCHAR(100),
            amount DECIMAL(18, 2),
            nameOrig VARCHAR(100),
            oldbalanceOrg DECIMAL(18, 2),
            newbalanceOrig DECIMAL(18, 2),
            nameDest VARCHAR(100),
            oldbalanceDest DECIMAL(18, 2),
            newbalanceDest DECIMAL(18, 2),
            isFraud INT,
            isFlaggedFraud INT
        )
    END
    """
    cursor.execute(create_table_sql)
    cursor.commit()
    logger.info("✅ Table created or already exists")


def insert_batch(
    cursor: pyodbc.Cursor,
    batch_df: pd.DataFrame,
    batch_num: int,
    total_batches: int
) -> None:
    """
    Inserts a batch of data into the database.
    
    Args:
        cursor: Database cursor
        batch_df: DataFrame containing batch data
        batch_num: Current batch number
        total_batches: Total number of batches
    """
    cursor.fast_executemany = True
    
    insert_sql = """
    INSERT INTO online_payment_fraud_detection (
        step, type, amount, nameOrig, oldbalanceOrg,
        newbalanceOrig, nameDest, oldbalanceDest,
        newbalanceDest, isFraud, isFlaggedFraud
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    data = list(batch_df.itertuples(index=False, name=None))
    
    cursor.executemany(insert_sql, data)
    cursor.commit()
    
    logger.info(f"✅ Inserted batch {batch_num}/{total_batches} ({len(batch_df)} rows)")


def load_csv_to_database(csv_path: str, chunksize: int = 10000) -> None:
    """
    Loads CSV data into SQL Server database in chunks.
    
    Args:
        csv_path: Path to CSV file
        chunksize: Number of rows per chunk
    """
    conn = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        create_table_if_not_exists(cursor)
        
        total_rows = 0
        batch_num = 0
        
        for chunk in read_csv_in_chunks(csv_path, chunksize):
            batch_num += 1
            insert_batch(cursor, chunk, batch_num, "?")
            total_rows += len(chunk)
        
        logger.info(f"✅ Successfully loaded {total_rows} rows in {batch_num} batches")
        
    except Exception as e:
        logger.error(f"❌ Error occurred: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Connection closed")


def main() -> None:
    csv_path = os.getenv("CSV_FILE_PATH")
    
    if not csv_path:
        logger.error("CSV_FILE_PATH environment variable not set")
        sys.exit(1)
    
    try:
        load_csv_to_database(csv_path)
    except Exception as e:
        logger.error(f"Load failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
