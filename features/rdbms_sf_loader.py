import sys
import logging
from typing import Dict, Any
from urllib.parse import quote_plus

import pandas as pd
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, upper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(path: str) -> Dict[str, Any]:
    """
    Loads configuration from YAML file.
    
    Args:
        path: Path to YAML config file
        
    Returns:
        Configuration dictionary
    """
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_sqlalchemy_conn_str(rdbms: Dict[str, str]) -> str:
    """
    Builds SQLAlchemy connection string with proper URL encoding.
    
    Args:
        rdbms: Dictionary containing RDBMS connection parameters
        
    Returns:
        SQLAlchemy connection string
    """
    username = quote_plus(rdbms['username'])
    password = quote_plus(rdbms['password'])
    host = rdbms['host']
    port = rdbms['port']
    database = rdbms['database']
    driver = rdbms['driver'].replace(' ', '+')
    
    return (
        f"mssql+pyodbc://{username}:{password}@{host}:{port}/"
        f"{database}?driver={driver}&Encrypt=yes&TrustServerCertificate=no"
    )


def fetch_data(
    sql_engine: Engine,
    table: str,
    chunksize: int = 100000
):
    """
    Fetches data from source database in chunks.
    
    Args:
        sql_engine: SQLAlchemy engine
        table: Table name to fetch
        chunksize: Number of rows per chunk
        
    Yields:
        DataFrame chunks
    """
    logger.info(f"Fetching data from {table} in chunks of {chunksize}")
    
    query = f"SELECT * FROM {table}"
    
    for chunk in pd.read_sql(query, sql_engine, chunksize=chunksize):
        logger.info(f"Retrieved chunk with {len(chunk)} records")
        yield chunk


def get_snowflake_session(config: Dict[str, str]) -> Session:
    """
    Creates Snowflake session from configuration.
    
    Args:
        config: Snowflake connection configuration
        
    Returns:
        Snowflake Session object
    """
    return Session.builder.configs({
        "account": config['account'],
        "user": config['user'],
        "password": config['password'],
        "role": config['role'],
        "warehouse": config['warehouse'],
        "database": config['database'],
        "schema": config['schema']
    }).create()


def run_data_load_engine(config: Dict[str, Any], use_chunking: bool = False) -> None:
    """
    Main data load function from RDBMS to Snowflake.
    
    Args:
        config: Configuration dictionary
        use_chunking: If True, process data in chunks (recommended for large datasets)
    """
    rdbms = config['rdbms']
    sf = config['snowflake']
    
    sql_engine = None
    session = None
    
    try:
        conn_str = build_sqlalchemy_conn_str(rdbms)
        sql_engine = create_engine(conn_str, fast_executemany=True)
        
        session = get_snowflake_session(sf)
        logger.info("✅ Connected to Snowflake")
        
        database = sf['database']
        schema = sf['schema']
        raw_table_full = f"{database}.{schema}.{sf['raw_table']}"
        transformed_table_full = f"{database}.{schema}.{sf['transformed_table']}"
        
        if use_chunking:
            first_chunk = True
            total_rows = 0
            
            for chunk in fetch_data(sql_engine, rdbms['table']):
                session.write_pandas(
                    chunk,
                    sf['raw_table'],
                    database=database,
                    schema=schema,
                    auto_create_table=first_chunk,
                    overwrite=first_chunk
                )
                total_rows += len(chunk)
                first_chunk = False
                logger.info(f"Uploaded chunk ({total_rows} rows total)")
            
            logger.info(f"✅ Data uploaded to {raw_table_full} ({total_rows} rows)")
        else:
            df = pd.read_sql(f"SELECT * FROM {rdbms['table']}", sql_engine)
            logger.info(f"✅ Retrieved {len(df)} records")
            
            session.write_pandas(
                df,
                sf['raw_table'],
                database=database,
                schema=schema,
                auto_create_table=True,
                overwrite=True
            )
            logger.info(f"✅ Data uploaded to {raw_table_full}")
        
        raw_df = session.table(raw_table_full)
        transformed_df = (
            raw_df
            .filter(col("isFraud") == 1)
            .with_column("nameDest_upper", upper(col("nameDest")))
        )
        
        transformed_df.write.mode("overwrite").save_as_table(
            sf['transformed_table'],
            database=database,
            schema=schema
        )
        logger.info(f"✅ Transformed data saved to {transformed_table_full}")
        
    except Exception as e:
        logger.error(f"❌ Data load failed: {e}")
        raise
    finally:
        if sql_engine:
            sql_engine.dispose()
            logger.info("SQLAlchemy engine disposed")
        if session:
            session.close()
            logger.info("Snowflake session closed")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python rdbms_sf_loader.py <path_to_config.yaml> [--chunked]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    use_chunking = "--chunked" in sys.argv
    
    try:
        config = load_config(config_path)
        run_data_load_engine(config, use_chunking)
        logger.info("✅ ETL pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
