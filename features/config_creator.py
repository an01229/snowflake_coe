import pandas as pd
import yaml
import argparse
import sys
from typing import Dict, Any
from pathlib import Path


def read_connection_details(file_path: str) -> pd.DataFrame:
    """
    Reads connection details from an Excel or CSV file.
    
    Args:
        file_path: Path to the input file (Excel or CSV)
        
    Returns:
        DataFrame containing connection details
        
    Raises:
        ValueError: If file format is unsupported or required columns are missing
    """
    path = Path(file_path)
    
    if path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif path.suffix == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Please provide Excel or CSV.")
    
    required_cols = ['ConnectionName', 'Type', 'Host', 'Port', 'Username', 'Password', 'Database']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return df


def create_yaml_file(dataframe: pd.DataFrame, output_file: str) -> None:
    """
    Creates a YAML file with connection parameters from the DataFrame.
    
    WARNING: This stores passwords in plaintext. Consider using environment
    variable references instead (e.g., ${DB_PASSWORD}).
    
    Args:
        dataframe: DataFrame containing connection details
        output_file: Path to the output YAML file
    """
    records = dataframe.to_dict(orient='records')
    
    connections = {}
    for record in records:
        connection_name = record['ConnectionName']
        connections[connection_name] = {
            'type': record['Type'],
            'host': record['Host'],
            'port': int(record['Port']),
            'username': record['Username'],
            'password': record['Password'],
            'database': record['Database'],
            'schema': record.get('Schema', None)
        }
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(connections, yaml_file, default_flow_style=False, allow_unicode=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Create YAML connection config from Excel/CSV file'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to input file (Excel or CSV)'
    )
    parser.add_argument(
        '-o', '--output',
        default='connections.yaml',
        help='Path to output YAML file (default: connections.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        connection_details = read_connection_details(args.input)
        create_yaml_file(connection_details, args.output)
        print(f"✅ YAML file created successfully: {args.output}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
