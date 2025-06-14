import json
import argparse
import os

DEFAULT_STRUCTURE = {
    "config": [],
    "templates": ["conn_param_template.tf", "conn_param_template.yaml"],
    "features": [
        "__init__.py",
        "main.py",
        "config_parser.py",
        "generator.py",
        "utils.py"
    ],
    "scripts": ["dq_wrapper.sh"],
    "DDLs": [],
    "param": [],
    "documentation": [],
    "README.md": "",
    "requirements.txt": ""
}

def load_custom_structure(template_path):
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load template from {template_path}: {e}")
        exit(1)

def generate_json(domain, project, output_file, custom_template=None):
    structure = custom_template if custom_template else DEFAULT_STRUCTURE
    full_structure = {
        "snowflake_coe": {
            domain: {
                project: structure
            }
        }
    }
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(script_dir, output_file)
    with open(output_path, "w") as f:
        json.dump(full_structure, f, indent=2)
    print(f"JSON structure saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate project structure JSON")
    parser.add_argument("-d", "--domain", required=True, help="Domain name (e.g., Data_engg)")
    parser.add_argument("-p", "--project", required=True, help="Project name (e.g., DB_API_testing)")
    parser.add_argument("-o", "--output", default=".generated_project.json", help="Output JSON file")
    parser.add_argument("-s", "--structure-template", help="Optional path to a custom project structure template")

    args = parser.parse_args()

    custom_structure = None
    if args.structure_template:
        custom_structure = load_custom_structure(args.structure_template)

    generate_json(args.domain, args.project, args.output, custom_structure)
