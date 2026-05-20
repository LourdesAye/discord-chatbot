"""
Project environment setup and directory configuration.
Provides functions to locate files, load environment variables,
and define absolute paths for project directories.
Provides methods to search for JSON files. 
"""

from pathlib import Path
from dotenv import load_dotenv
import os
from typing import List, Optional
from database.models.clase_ruta import Ruta


def find_file_in_parents(file_name: str, start: Optional[Path] = None) -> Path:
    """
    Search for a file by climbing up the directory tree.

    Args:
        file_name (str): Name of the file to search for.
        start (Path, optional): Starting directory. Defaults to the script location or current working directory.

    Returns:
        Path: The full path to the file if found.

    Raises:
        FileNotFoundError: If the file is not found in any parent directory.
    """
    if start is None:
        try:
            start = Path(__file__).resolve().parent
        except NameError:
            start = Path.cwd()

    current_dir = start

    while True:
        candidate_path = current_dir / file_name
        if candidate_path.exists() and candidate_path.is_file():
            return candidate_path
        if current_dir.parent == current_dir:
            raise FileNotFoundError(
                f" ❌ Could not find {file_name} in any parent directory of {start}"
            )
        current_dir = current_dir.parent


def setup_environment(
    file_name: str = ".env",
) -> Path:
    """
    Initialize the project environment by loading variables from a .env file.

    Args:
        file_name (str, optional): Name of the environment file. Defaults to ".env".

    Returns:
        Path: The root directory of the project (parent of the .env file).

    Raises:
        FileNotFoundError: If the .env file is not found in any parent directory.
    """
    env_file_path = find_file_in_parents(file_name)
    load_dotenv(dotenv_path=env_file_path)
    return env_file_path.parent


PROJECT_ROOT = setup_environment()

LOG_DIR = os.getenv("LOG_DIR", "logs")  
JSON_DIR = os.getenv("JSON_DIR", "json")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma")
DOCS_DIR = os.getenv("DOCS_DIR", "docs")

LOG_DIR_ABS = PROJECT_ROOT / LOG_DIR
JSON_DIR_ABS = PROJECT_ROOT / JSON_DIR
CHROMA_DIR_ABS = PROJECT_ROOT / CHROMA_DIR

def get_files_by_pattern(base_dir: Path, search_pattern: str) -> List[Path]:
    """
    Find all files in base_dir and subdirectories that match the search pattern.

    Args:
        base_dir (Path): The directory to search in.
        search_pattern (str): The pattern to match against file names.

    Returns:
        List[Path]: A list of file paths that match the search pattern.
    """
    return list(base_dir.rglob(search_pattern))

def is_regular_file(file: Path) -> bool:
    """
    Check if the given path is a regular file (not a directory or symlink).

    Args:
        file (Path): The path to check.
    
    Returns:
        bool: True if it's a regular file, False otherwise.
    """
    return file.is_file()

def get_relative_path(file: Path, base_dir: Path) -> Path:
    """
    Get the relative path of a file with respect to the base directory.

    Args:
        file (Path) : The file path.
        base_dir (Path) : base directory to calculate relative path from. 
    """
    return file.relative_to(base_dir)


def calculate_depth(relative_path: Path) -> int:
    """
    Calculate the depth of a relative path (number of parent directories).

    Args:
        relative_path (Path): The relative path to calculate depth for.

    Returns:
        int: The depth of the relative path.

    """
    return len(relative_path.parents)

class FileSearcher:
    """
    Class allow to search files inside project structure.
    """

    def get_json_paths(self, base_dir: Path = None) -> List[Ruta]:
        """
        Retrieve all JSON file paths within the given directory.

        Args:
            base_dir (Path, optional): The base directory to search for JSON files.
                                        If not provided, defaults to JSON_DIR_ABS.
        
        Returns: 
            List[Ruta]: A list of Ruta objects representing the found JSON file paths.
        """
        base_dir = base_dir or JSON_DIR_ABS
        if not base_dir.exists():
            raise FileNotFoundError(f"Directory does not exist: {base_dir}")

        results: List[Ruta] = []
        search_pattern = os.getenv("FILE_NAME", "chat.json")
        max_depth = int(os.getenv("MAX_DEPTH", 999))

        files = get_files_by_pattern(base_dir, search_pattern)

        for file in files:
            if not is_regular_file(file):
                continue

            relative_path = get_relative_path(file, base_dir)
            depth = calculate_depth(relative_path)

            if depth <= max_depth:
                ruta_obj = Ruta(file)
                if ruta_obj.existe(): 
                    results.append(ruta_obj)

        return results
