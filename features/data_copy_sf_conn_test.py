from snowflake.snowpark import Session

snowflake_config = {
    "account": "anblicksorg-anblickspartner",
    "user": "saikrishna.c",
    "password": "Captainmaverick#0044",
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

