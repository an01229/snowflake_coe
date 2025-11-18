import os
import json
import argparse
import shutil
import sys
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OperationResult:
    """Tracks the results of structure operations."""
    created_dirs: List[str] = field(default_factory=list)
    created_files: List[str] = field(default_factory=list)
    skipped_items: List[str] = field(default_factory=list)
    deleted_items: List[str] = field(default_factory=list)
    log_lines: List[str] = field(default_factory=list)
    
    def log(self, message: str) -> None:
        """Log a message to both console and internal log."""
        logger.info(message)
        self.log_lines.append(message)
    
    def summary(self) -> str:
        """Generate summary string."""
        return (
            f"\n===== SUMMARY =====\n"
            f"Created dirs: {len(self.created_dirs)}\n"
            f"Created files: {len(self.created_files)}\n"
            f"Skipped: {len(self.skipped_items)}\n"
            f"Deleted: {len(self.deleted_items)}"
        )

def create_structure(
    base_path: Path,
    structure: Dict[str, Any],
    result: OperationResult,
    dry_run: bool = False
) -> None:
    """
    Recursively creates directory structure from dictionary.
    
    Args:
        base_path: Base directory path
        structure: Dictionary defining the structure
        result: OperationResult to track operations
        dry_run: If True, only log what would be done
    """
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            if path.exists():
                result.skipped_items.append(str(path))
                result.log(f"[SKIP] Directory exists: {path}")
            else:
                if not dry_run:
                    path.mkdir(parents=True, exist_ok=True)
                result.created_dirs.append(str(path))
                result.log(f"[CREATE] Directory: {path}")
            
            create_structure(path, content, result, dry_run)
            
        elif isinstance(content, list):
            if path.exists():
                result.skipped_items.append(str(path))
                result.log(f"[SKIP] Directory exists: {path}")
            else:
                if not dry_run:
                    path.mkdir(parents=True, exist_ok=True)
                result.created_dirs.append(str(path))
                result.log(f"[CREATE] Directory: {path}")
            
            for file_name in content:
                file_path = path / file_name
                if file_path.exists():
                    result.skipped_items.append(str(file_path))
                    result.log(f"[SKIP] File exists: {file_path}")
                else:
                    if not dry_run:
                        file_path.touch()
                    result.created_files.append(str(file_path))
                    result.log(f"[CREATE] File: {file_path}")
                    
        elif isinstance(content, str):
            if path.exists():
                result.skipped_items.append(str(path))
                result.log(f"[SKIP] File exists: {path}")
            else:
                if not dry_run:
                    path.touch()
                result.created_files.append(str(path))
                result.log(f"[CREATE] File: {path}")

def backup_and_delete(
    path: Path,
    target_root: Path,
    backup_root: str,
    result: OperationResult,
    dry_run: bool = False
) -> None:
    """
    Backs up and deletes a file or directory.
    
    Args:
        path: Path to delete
        target_root: Root path for calculating relative paths
        backup_root: Name of backup directory
        result: OperationResult to track operations
        dry_run: If True, only log what would be done
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rel_path = path.relative_to(target_root)
    backup_path = target_root / backup_root / f"{rel_path}_{timestamp}"
    
    try:
        if not dry_run:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            if path.is_dir():
                if not dry_run:
                    shutil.copytree(path, backup_path)
                    shutil.rmtree(path)
            elif path.is_file():
                if not dry_run:
                    shutil.copy2(path, backup_path)
                    path.unlink()
        
        result.deleted_items.append(str(path))
        result.log(f"[DELETE] Backed up to {backup_path}: {path}")
        
    except Exception as e:
        result.log(f"[ERROR] Failed to delete {path}: {e}")

def delete_structure(
    base_path: Path,
    structure: Dict[str, Any],
    target_root: Path,
    backup_root: str,
    result: OperationResult,
    dry_run: bool = False
) -> None:
    """
    Recursively deletes directory structure.
    
    Args:
        base_path: Base directory path
        structure: Dictionary defining the structure to delete
        target_root: Root path for backups
        backup_root: Name of backup directory
        result: OperationResult to track operations
        dry_run: If True, only log what would be done
    """
    for name, content in structure.items():
        path = base_path / name
        result.log(f"[CHECK] Checking for deletion: {path}")
        
        if path.exists():
            if isinstance(content, dict):
                delete_structure(path, content, target_root, backup_root, result, dry_run)
            
            backup_and_delete(path, target_root, backup_root, result, dry_run)
            
        elif isinstance(content, dict):
            delete_structure(path, content, target_root, backup_root, result, dry_run)



def write_log_to_file(result: OperationResult, log_file: str = "struct_gen_job.log") -> None:
    """
    Writes operation log to file.
    
    Args:
        result: OperationResult containing log lines
        log_file: Path to log file
    """
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(f"\n\n=== Operation on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        for line in result.log_lines:
            f.write(line + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or delete repository structure from JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create structure
  %(prog)s -j project.json -o c -t /path/to/target
  
  %(prog)s -j project.json -o d -t /path/to/target
  
  %(prog)s -j project.json -o c -t /path/to/target --dry-run
        """
    )
    parser.add_argument(
        "-j", "--json_file",
        required=True,
        help="Path to the JSON structure file"
    )
    parser.add_argument(
        "-o", "--operation",
        required=True,
        choices=["c", "d"],
        help="Operation: 'c' for create, 'd' for delete"
    )
    parser.add_argument(
        "-t", "--target-path",
        default=os.getcwd(),
        help="Target root path where structure will be created or deleted (default: current directory)"
    )
    parser.add_argument(
        "--backup-root",
        default="__backups",
        help="Name of backup directory for delete operations (default: __backups)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        target_path = Path(args.target_path).resolve()
        json_path = Path(args.json_file)
        
        if not json_path.exists():
            logger.error(f"JSON file not found: {args.json_file}")
            sys.exit(1)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            structure = json.load(f)
        
        logger.info(f"Target path: {target_path}")
        logger.info(f"JSON structure top keys: {list(structure.keys())}")
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        result = OperationResult()
        
        if args.operation == 'c':
            create_structure(target_path, structure, result, args.dry_run)
        elif args.operation == 'd':
            delete_structure(
                target_path,
                structure,
                target_path,
                args.backup_root,
                result,
                args.dry_run
            )
        
        print(result.summary())
        
        if not args.dry_run:
            write_log_to_file(result)
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
