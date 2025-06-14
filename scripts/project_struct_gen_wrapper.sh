#!/bin/bash

# Usage:
# ./project_struct_gen_wrapper.sh -d Data_engg -p DB_API_testing -t /target/path -o c -s /path/to/template.json

while getopts ":d:p:t:o:s:" opt; do
  case $opt in
    d) DOMAIN=$OPTARG ;;
    p) PROJECT=$OPTARG ;;
    t) TARGET=$OPTARG ;;
    o) OPERATION=$OPTARG ;;
    s) TEMPLATE=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; exit 1 ;;
  esac
done

if [[ -z "$DOMAIN" || -z "$PROJECT" || -z "$OPERATION" ]]; then
  echo "Usage: $0 -d <domain> -p <project> -t <target_path> -o <c|d> [-s <structure_template.json>]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_JSON="$SCRIPT_DIR/.generated_project.json"

# Generate JSON using custom structure if provided
if [[ -n "$TEMPLATE" ]]; then
  python3 "$SCRIPT_DIR/generate_project_json.py" -d "$DOMAIN" -p "$PROJECT" -o "$TEMP_JSON" -s "$TEMPLATE"
else
  python3 "$SCRIPT_DIR/generate_project_json.py" -d "$DOMAIN" -p "$PROJECT" -o "$TEMP_JSON"
fi

echo "Target project path passed to project structure manager: $TARGET"

# Call the project structure manager
python3 "$SCRIPT_DIR/manage_project_struct.py" -o "$OPERATION" -j "$TEMP_JSON" -t "$TARGET"
