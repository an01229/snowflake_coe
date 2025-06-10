import os
import json
import argparse

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        elif isinstance(content, list):
            os.makedirs(path, exist_ok=True)
            for file in content:
                open(os.path.join(path, file), "a").close()
        elif isinstance(content, str):  # For standalone files like .gitignore
            open(os.path.join(base_path, name), "a").close()

def main():
    parser = argparse.ArgumentParser(description="Create repo structure from JSON.")
    parser.add_argument("json_file", help="Path to the JSON structure file")
    args = parser.parse_args()

    # Load JSON structure
    with open(args.json_file, 'r') as f:
        structure = json.load(f)

    # Create structure
    create_structure(os.getcwd(), structure)
    print("✅ Project structure created successfully.")

if __name__ == "__main__":
    main()
