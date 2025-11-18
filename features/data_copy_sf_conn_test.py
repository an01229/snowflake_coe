import os
import sys
from snowflake.snowpark import Session


def get_snowflake_session() -> Session:
    """
    Creates Snowflake session from environment variables.
    
    Returns:
        Snowflake Session object
        
    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = [
        "SF_ACCOUNT", "SF_USER", "SF_PASSWORD", 
        "SF_ROLE", "SF_WAREHOUSE", "SF_DATABASE", "SF_SCHEMA"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    config = {
        "account": os.getenv("SF_ACCOUNT"),
        "user": os.getenv("SF_USER"),
        "password": os.getenv("SF_PASSWORD"),
        "role": os.getenv("SF_ROLE"),
        "warehouse": os.getenv("SF_WAREHOUSE"),
        "database": os.getenv("SF_DATABASE"),
        "schema": os.getenv("SF_SCHEMA")
    }
    
    return Session.builder.configs(config).create()


def main() -> None:
    """Simple CLI test runner."""
    try:
        session = get_snowflake_session()
        print("✅ Connected to Snowflake!")
        
        result = session.sql("SELECT CURRENT_VERSION()").collect()
        print(f"Snowflake version: {result[0][0]}")
        
        session.close()
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

