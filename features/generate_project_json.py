import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_STRUCTURE = {
    "config": ["test.csv"],
    "templates": ["conn_param_template.tf", "conn_param_template.yaml"],
    "features": [
        "__init__.py",
        "main.py",
        "config_parser.py",
        "generator.py",
        "utils.py"
    ],
    "scripts": ["dq_wrapper.sh"],
    "DDLs": ["test.sql"],
    "param": ["test_params.env"],
    "documentation": ["test.md"],
}


def load_custom_structure(template_path: str) -> Dict[str, Any]:
    """
    Loads custom project structure from JSON template file.
    
    Args:
        template_path: Path to JSON template file
        
    Returns:
        Dictionary containing project structure
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        json.JSONDecodeError: If template is not valid JSON
        ValueError: If template structure is invalid
    """
    path = Path(template_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        structure = json.load(f)
    
    if not isinstance(structure, dict):
        raise ValueError("Template must be a JSON object (dictionary)")
    
    return structure


def validate_structure(structure: Dict[str, Any]) -> None:
    """
    Validates that the structure is well-formed.
    
    Args:
        structure: Project structure dictionary
        
    Raises:
        ValueError: If structure is invalid
    """
    for key, value in structure.items():
        if not isinstance(value, (list, dict)):
            raise ValueError(
                f"Invalid structure: '{key}' must be a list or dict, got {type(value)}"
            )
        
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise ValueError(f"All items in '{key}' list must be strings")


def generate_json(
    domain: str,
    project: str,
    output_file: str,
    custom_template: Optional[Dict[str, Any]] = None,
    output_dir: Optional[str] = None
) -> Path:
    """
    Generates project structure JSON file.
    
    Args:
        domain: Domain name (e.g., 'Data_engg')
        project: Project name (e.g., 'DB_API_testing')
        output_file: Output filename
        custom_template: Optional custom structure (uses DEFAULT_STRUCTURE if None)
        output_dir: Optional output directory (uses current dir if None)
        
    Returns:
        Path to created JSON file
    """
    structure = custom_template if custom_template else DEFAULT_STRUCTURE
    
    validate_structure(structure)
    
    full_structure = {
        domain: {
            project: structure
        }
    }
    
    if output_dir:
        output_path = Path(output_dir) / output_file
    else:
        output_path = Path(output_file)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(full_structure, f, indent=2)
    
    print(f"✅ JSON structure saved to {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate project structure JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -d Data_engg -p MyProject
  %(prog)s -d Data_engg -p MyProject -o custom.json
  %(prog)s -d Data_engg -p MyProject -s template.json --output-dir /path/to/dir
        """
    )
    parser.add_argument(
        "-d", "--domain",
        required=True,
        help="Domain name (e.g., Data_engg)"
    )
    parser.add_argument(
        "-p", "--project",
        required=True,
        help="Project name (e.g., DB_API_testing)"
    )
    parser.add_argument(
        "-o", "--output",
        default=".generated_project.json",
        help="Output JSON filename (default: .generated_project.json)"
    )
    parser.add_argument(
        "-s", "--structure-template",
        help="Optional path to a custom project structure template (JSON)"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    try:
        custom_structure = None
        if args.structure_template:
            custom_structure = load_custom_structure(args.structure_template)
        
        generate_json(
            args.domain,
            args.project,
            args.output,
            custom_structure,
            args.output_dir
        )
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
