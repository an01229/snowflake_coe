# rdbms_to_snowflake.py
import pandas as pd
import yaml
import sys
from sqlalchemy import create_engine
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, upper

# Load config from path passed as argument
def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Build SQLAlchemy connection string
def build_sqlalchemy_conn_str(rdbms):
    return (
        f"mssql+pyodbc://{rdbms['username']}:{rdbms['password']}@{rdbms['host']}:{rdbms['port']}/"
        f"{rdbms['database']}?driver={rdbms['driver'].replace(' ', '+')}&Encrypt=yes&TrustServerCertificate=no"
    )

# Fetch data from source
def fetch_data(sql_engine, table):
    print("Fetching data from RDBMS...")
    df = pd.read_sql(f"SELECT * FROM {table}", sql_engine)
    print(f"✅ Retrieved {len(df)} records.")
    return df

# Snowflake session setup
def get_snowflake_session(config):
    return Session.builder.configs({
        "account": config['account'],
        "user": config['user'],
        "password": config['password'],
        "role": config['role'],
        "warehouse": config['warehouse'],
        "database": config['database'],
        "schema": config['schema']
    }).create()

# Main data load function
def run_data_load_engine(config):
    rdbms = config['rdbms']
    sf = config['snowflake']

    sql_engine = create_engine(build_sqlalchemy_conn_str(rdbms))
    df = fetch_data(sql_engine, rdbms['table'])

    session = get_snowflake_session(sf)
    print("Connected to Snowflake.")

    session.write_pandas(df, sf['raw_table'], auto_create_table=True, overwrite=True)
    print(f"Data uploaded to Snowflake table: {sf['raw_table']}")

    raw_df = session.table(sf['raw_table'])
    transformed_df = (
        raw_df
        .filter(col("isFraud") == 1)
        .with_column("nameDest_upper", upper(col("nameDest")))
    )

    transformed_df.write.mode("overwrite").save_as_table(sf['transformed_table'])
    print(f"Transformed data saved to: {sf['transformed_table']}")
    session.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rdbms_to_snowflake.py <path_to_config.yaml>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    config = load_config(config_path)
    run_data_load_engine(config)
