import pandas as pd
import yaml

def read_connection_details(file_path):
    """
    Reads connection details from an Excel or CSV file.
    :param file_path: Path to the input file (Excel or CSV).
    :return: DataFrame containing connection details.
    """
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide an Excel or CSV file.")

def create_yaml_file(dataframe, output_file):
    """
    Creates a YAML file with connection parameters from the DataFrame.
    :param dataframe: DataFrame containing connection details.
    :param output_file: Path to the output YAML file.
    """
    connections = {}
    for _, row in dataframe.iterrows():
        connection_name = row['ConnectionName']
        connections[connection_name] = {
            'type': row['Type'],
            'host': row['Host'],
            'port': row['Port'],
            'username': row['Username'],
            'password': row['Password'],
            'database': row['Database'],
            'schema': row.get('Schema', None)  # Optional field
        }

    with open(output_file, 'w') as yaml_file:
        yaml.dump(connections, yaml_file, default_flow_style=False)

def main():
    input_file = 'connection_details.xlsx'  # Replace with your file path
    output_file = 'connections.yaml'  # Replace with your desired output file path

    # Read connection details from the input file
    connection_details = read_connection_details(input_file)

    # Create YAML file with connection parameters
    create_yaml_file(connection_details, output_file)
    print(f"YAML file created successfully: {output_file}")

if __name__ == "__main__":
    main()