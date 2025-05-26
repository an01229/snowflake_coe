from snowflake.snowpark import Session

session = Session.builder.configs({
    "account": "anblickspartner.anblicksorg",
    "user": "saikrishna.c",
    "password": "SaiPassword#2025",
    "role": "COE_DEV_ROLE",
    "warehouse": "ANBLICKS_H2S_WH",
    "database": "COE_DATABASE",
    "schema": "COE_POC_SCHEMA"
}).create()

print("✅ Connected to Snowflake!")
session.close()
