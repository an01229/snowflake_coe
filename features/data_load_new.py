import os
import sys
import logging
import urllib.parse

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_sqlalchemy_engine():
    """
    Creates SQLAlchemy engine using environment variables.
    
    Returns:
        SQLAlchemy engine
    """
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER_HOST')};"
        f"DATABASE={os.getenv('SQL_SERVER_DB')};"
        f"UID={os.getenv('SQL_SERVER_USER')};"
        f"PWD={os.getenv('SQL_SERVER_PASSWORD')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        fast_executemany=True
    )
    
    logger.info("✅ SQLAlchemy engine created")
    return engine


def load_csv_to_sql(
    csv_path: str,
    table_name: str,
    chunksize: int = 10000,
    if_exists: str = "replace"
) -> None:
    """
    Loads CSV data to SQL Server using streaming approach.
    
    Args:
        csv_path: Path to CSV file
        table_name: Target table name
        chunksize: Rows per chunk for reading and writing
        if_exists: 'replace', 'append', or 'fail'
    """
    engine = None
    
    try:
        engine = get_sqlalchemy_engine()
        
        total_rows = 0
        chunk_num = 0
        
        for chunk in pd.read_csv(csv_path, chunksize=chunksize):
            chunk_num += 1
            
            if 'amount' in chunk.columns:
                chunk["amount"] = pd.to_numeric(chunk["amount"], errors="coerce")
            if 'step' in chunk.columns:
                chunk["step"] = pd.to_numeric(chunk["step"], errors="coerce")
            if 'isFraud' in chunk.columns:
                chunk["isFraud"] = pd.to_numeric(chunk["isFraud"], errors="coerce")
            if 'isFlaggedFraud' in chunk.columns:
                chunk["isFlaggedFraud"] = pd.to_numeric(chunk["isFlaggedFraud"], errors="coerce")
            
            chunk.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace" if chunk_num == 1 else "append",
                index=False,
                chunksize=1000,
                method="multi"
            )
            
            total_rows += len(chunk)
            logger.info(f"✅ Chunk {chunk_num} uploaded ({len(chunk)} rows, {total_rows} total)")
        
        logger.info(f"✅ Successfully loaded {total_rows} rows in {chunk_num} chunks")
        
    except Exception as e:
        logger.error(f"❌ Failed to load data: {e}")
        raise
    finally:
        if engine:
            engine.dispose()
            logger.info("Engine disposed")


def main() -> None:
    csv_path = os.getenv("CSV_FILE_PATH")
    table_name = os.getenv("TABLE_NAME", "online_payment_fraud_detection")
    
    if not csv_path:
        logger.error("CSV_FILE_PATH environment variable not set")
        sys.exit(1)
    
    try:
        load_csv_to_sql(csv_path, table_name)
    except Exception as e:
        logger.error(f"Load failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
