#!/bin/bash

# Usage: ./project_struct_gen_wrapper.sh -o c -j repo_struct.json

while getopts ":o:j:" opt; do
  case $opt in
    o)
      OPERATION=$OPTARG
      ;;
    j)
      JSON_FILE=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG"
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument."
      exit 1
      ;;
  esac
done

if [[ -z "$OPERATION" || -z "$JSON_FILE" ]]; then
  echo "Usage: $0 -o <c|d> -j <json_file>"
  exit 1
fi

python3 folder_creation.py -o "$OPERATION" -j "$JSON_FILE"