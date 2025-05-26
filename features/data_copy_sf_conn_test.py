from snowflake.snowpark import Session

snowflake_config = {
    "account": "anblickspartner",
    "organization": "anblicksorg",             # ✅ add this
    "region": "us-west-2",                     # ✅ required for SSL match
    "host": "anblickspartner.anblicksorg.snowflakecomputing.com",  # optional fallback
    "user": "saikrishna.c",
    "password": "SaiPassword#2025",
    "role": "COE_DEV_ROLE",
    "warehouse": "ANBLICKS_H2S_WH",
    "database": "COE_DATABASE",
    "schema": "COE_POC_SCHEMA"
}

try:
    session = Session.builder.configs(snowflake_config).create()
    print("✅ Connected to Snowflake!")
    session.close()
except Exception as e:
    print("❌ Snowflake connection failed:", e)
    exit()
