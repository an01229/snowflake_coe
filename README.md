# snowflake_coe
# Snowflake COE Project Structure Automation Framework

This framework automates the creation and deletion of standardized project folder structures under the **Snowflake Center of Excellence (COE)**. It is designed to support multiple domains (e.g., `AI_ML`, `Data_engg`, `Analytics`, `Migration`) and multiple projects within each domain — with a consistent template across all.

---

## Features

- Auto-generates nested folder and file structures using a dynamic JSON template
- Supports deletion of existing project structures with backup
- Works domain-wise and project-wise (e.g., `Data_engg → DB_API_automation`)
- Creates backups before deletion in `__backups/` directory
- Supports custom structure templates (override the default layout)
- Fully logged via `structure_manage.log`

---

## Default Project Structure

Each project created will follow this structure:

project_root/
└── snowflake_coe/
└── <DOMAIN>/
    └── <PROJECT_NAME>/
        ├── config/
        ├── templates/
        ├── features/
        ├── scripts/
        ├── DDLs/
        ├── param/
        ├── documentation/
        ├── README.md
        ├── requirements.txt



You can customize this structure using a JSON template.

---


### Usage:
### Create a Project Structure

```
bash project_struct_gen_wrapper.sh \
  -d Data_engg \
  -p DB_API_automation \
  -t "/Users/you/path/to/snowflake_coe" \
  -o c
```

### Delete a Project Structure (with Backup)
```bash project_struct_gen_wrapper.sh \
  -d Data_engg \
  -p DB_API_automation \
  -t "/Users/you/path/to/snowflake_coe" \
  -o d
```

### Use a Custom Structure Template
```bash project_struct_gen_wrapper.sh \
  -d AI_ML \
  -p ModelBuilder \
  -t "/Users/you/snowflake_coe" \
  -o c \
  -s ./custom_structure.json
```

### How It Works

-- generate_project_json.py dynamically builds the JSON structure based on domain and project.
-- The generated JSON is passed to manage_project_struct.py.
-- The manager script:
-- Creates directories and files if -o c
-- Deletes the structure with backup if -o d
-- Everything is logged in structure_manage.log.

### Requirements

-- Python 3.7+
-- Compatible with macOS/Linux
-- No external dependencies required

### TODOs / Enhancements

-- dry-run mode
-- force delete without backup
-- Compression of deleted backups (.zip)
-- Integration into CI/CD via azure DevOps