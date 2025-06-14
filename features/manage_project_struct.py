import os
import json
import argparse
import shutil
from datetime import datetime

created_dirs = []
created_files = []
skipped_items = []
deleted_items = []
log_lines = []
backup_root = "__backups"

def log(message):
    print(message)
    log_lines.append(message)

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            if not os.path.exists(path):
                os.makedirs(path)
                created_dirs.append(path)
                log(f"Created directory: {path}")
            else:
                skipped_items.append(path)
                log(f"Skipped existing directory: {path}")
            create_structure(path, content)
        elif isinstance(content, list):
            if not os.path.exists(path):
                os.makedirs(path)
                created_dirs.append(path)
                log(f"Created directory: {path}")
            else:
                skipped_items.append(path)
                log(f"Skipped existing directory: {path}")
            for file in content:
                file_path = os.path.join(path, file)
                if not os.path.exists(file_path):
                    open(file_path, "a").close()
                    created_files.append(file_path)
                    log(f"Created file: {file_path}")
                else:
                    skipped_items.append(file_path)
                    log(f"Skipped existing file: {file_path}")
        elif isinstance(content, str):
            file_path = os.path.join(base_path, name)
            if not os.path.exists(file_path):
                open(file_path, "a").close()
                created_files.append(file_path)
                log(f"Created file: {file_path}")
            else:
                skipped_items.append(file_path)
                log(f"Skipped existing file: {file_path}")

def backup_and_delete(path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rel_path = os.path.relpath(path, os.getcwd())
    backup_path = os.path.join(backup_root, f"{rel_path}_{timestamp}")

    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    try:
        if os.path.isdir(path):
            shutil.copytree(path, backup_path)
            shutil.rmtree(path)
        elif os.path.isfile(path):
            shutil.copy2(path, backup_path)
            os.remove(path)
        deleted_items.append(path)
        log(f"Deleted (backup at {backup_path}): {path}")
    except Exception as e:
        log(f"Failed to delete {path}: {e}")

def delete_structure(base_path, structure):
    for name in structure.keys():
        path = os.path.join(base_path, name)
        if os.path.exists(path):
            backup_and_delete(path)

def write_log_to_file():
    log_file = "struct_gen_job.log"
    with open(log_file, "a") as f:
        f.write("\n\n=== Operation on {} ===\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        for line in log_lines:
            f.write(line + "\n")

def main():
    parser = argparse.ArgumentParser(description="Create or delete repo structure from JSON.")
    parser.add_argument("-j", "--json_file", required=True, help="Path to the JSON structure file")
    parser.add_argument("-o", "--operation", required=True, choices=["c", "d"], help="Operation: 'c' for create, 'd' for delete")

    args = parser.parse_args()

    with open(args.json_file, 'r') as f:
        structure = json.load(f)

    if args.operation == 'c':
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # go 1 level up from script
        create_structure(project_root, structure)
    elif args.operation == 'd':
        delete_structure(os.getcwd(), structure)

    log("\n===== Project structure creation summary =====")
    log(f"Created directories: {len(created_dirs)}")
    log(f"Created files: {len(created_files)}")
    log(f"Skipped: {len(skipped_items)}")
    log(f"Deleted: {len(deleted_items)}")

    write_log_to_file()

if __name__ == "__main__":
    main()