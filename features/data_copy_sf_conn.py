import os
import sys
import logging
from typing import Optional

import pandas as pd
import pyodbc
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, upper, when

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_sql_server_connection() -> pyodbc.Connection:
    """
    Establishes connection to SQL Server using environment variables.
    
    Required environment variables:
        SQL_SERVER_HOST, SQL_SERVER_DB, SQL_SERVER_USER, SQL_SERVER_PASSWORD
        
    Returns:
        pyodbc Connection object
        
    Raises:
        Exception: If connection fails
    """
    connection_string = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={os.getenv("SQL_SERVER_HOST")};'
        f'DATABASE={os.getenv("SQL_SERVER_DB")};'
        f'UID={os.getenv("SQL_SERVER_USER")};'
        f'PWD={os.getenv("SQL_SERVER_PASSWORD")};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
        f'Connection Timeout=60;'
    )
    
    conn = pyodbc.connect(connection_string)
    logger.info("✅ Connected to SQL Server")
    return conn


def get_snowflake_session() -> Session:
    """
    Creates Snowflake session using environment variables.
    
    Required environment variables:
        SF_ACCOUNT, SF_USER, SF_PASSWORD, SF_ROLE, SF_WAREHOUSE, SF_DATABASE, SF_SCHEMA
        
    Returns:
        Snowflake Session object
    """
    config = {
        "account": os.getenv("SF_ACCOUNT"),
        "user": os.getenv("SF_USER"),
        "password": os.getenv("SF_PASSWORD"),
        "role": os.getenv("SF_ROLE"),
        "warehouse": os.getenv("SF_WAREHOUSE"),
        "database": os.getenv("SF_DATABASE"),
        "schema": os.getenv("SF_SCHEMA")
    }
    
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    session = Session.builder.configs(config).create()
    logger.info("✅ Connected to Snowflake")
    return session


def load_staging_data(
    session: Session,
    df: pd.DataFrame,
    staging_table: str,
    database: str,
    schema: str
) -> None:
    """
    Writes data to Snowflake staging table.
    
    Args:
        session: Snowflake session
        df: DataFrame to write
        staging_table: Name of staging table
        database: Database name
        schema: Schema name
    """
    full_table_name = f"{database}.{schema}.{staging_table}"
    
    session.write_pandas(
        df=df,
        table_name=staging_table,
        database=database,
        schema=schema,
        auto_create_table=True,
        overwrite=True
    )
    logger.info(f"✅ Data written to {full_table_name}")


def transform_and_load_final(
    session: Session,
    staging_table: str,
    final_table: str,
    database: str,
    schema: str
) -> None:
    """
    Applies transformations and writes to final table.
    
    Args:
        session: Snowflake session
        staging_table: Source staging table name
        final_table: Target final table name
        database: Database name
        schema: Schema name
    """
    staging_full = f"{database}.{schema}.{staging_table}"
    final_full = f"{database}.{schema}.{final_table}"
    
    sf_df = session.table(staging_full)
    logger.info(f"Loaded data from {staging_full}")
    
    transformed_df = (
        sf_df
        .with_column("AMOUNT_USD", col("AMOUNT") * 1.0)
        .with_column("TYPE_UPPER", upper(col("TYPE")))
        .with_column("IS_HIGH_VALUE", when(col("AMOUNT") > 10000, 1).otherwise(0))
    )
    
    transformed_df.write.mode("overwrite").save_as_table(final_table)
    logger.info(f"✅ Transformed data written to {final_full}")


def run_etl_pipeline(
    source_table: str = "online_payment_fraud_detection",
    staging_table: str = "online_payment_fraud_staging",
    final_table: str = "online_payment_fraud_final"
) -> None:
    """
    Runs the complete ETL pipeline from SQL Server to Snowflake.
    
    Args:
        source_table: SQL Server source table name
        staging_table: Snowflake staging table name
        final_table: Snowflake final table name
    """
    sql_conn: Optional[pyodbc.Connection] = None
    session: Optional[Session] = None
    
    try:
        sql_conn = get_sql_server_connection()
        
        df = pd.read_sql(f"SELECT * FROM {source_table}", sql_conn)
        logger.info(f"Retrieved {len(df)} records from SQL Server")
        
        session = get_snowflake_session()
        
        database = os.getenv("SF_DATABASE")
        schema = os.getenv("SF_SCHEMA")
        
        load_staging_data(session, df, staging_table, database, schema)
        
        transform_and_load_final(session, staging_table, final_table, database, schema)
        
        logger.info("✅ ETL pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {e}")
        raise
    finally:
        if sql_conn:
            sql_conn.close()
            logger.info("SQL Server connection closed")
        if session:
            session.close()
            logger.info("Snowflake session closed")


def main() -> None:
    try:
        run_etl_pipeline()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
