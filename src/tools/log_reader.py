import os
from pathlib import Path

from langchain_core.tools import tool

from ..config import Config


@tool
def read_log_file(file_name: str) -> str:
    """
    Read the contents of a log file.
    Input: file_name (str): The name of the log file to read.
    Example: app.log, error_log.log

    Return a string containing the contents of the log file.
    """
    log_path = os.path.join(Config.LOG_DIRECTORY, file_name)
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            content = file.read()

        file_size = os.path.getsize(log_path)
        line_count = content.count('\n') + 1

        return f"Log file '{file_name}' read successfully. Size: {file_size} bytes, Lines: {line_count}.\n\n{content}"


    except FileNotFoundError:
        return f"Error: Log file '{file_name}' not found in directory '{Config.LOG_DIRECTORY}'."
    
    except PermissionError:
        return f"Error: Permission denied when trying to read log file '{file_name}'."
    
    except Exception as e:
        return f"Error: An unexpected error occurred while reading log file '{file_name}': {str(e)}"
    

@tool
def list_log_files() -> str:
    """
    List all available log files in the specified log directory.

    Return: String containing list of available log files with their sizes
    """
    log_dir = Path(Config.LOG_DIRECTORY)
    
    if not log_dir.exists() or not log_dir.is_dir():
        return f"Error: Log directory '{Config.LOG_DIRECTORY}' does not exist or is not a directory."

    try:
        log_files = [f for f in log_dir.iterdir() if f.is_file() and f.suffix == '.log']

        if not log_files:
            return f"No log files found in directory '{Config.LOG_DIRECTORY}'."

        result = f"Available log files in '{Config.LOG_DIRECTORY}':\n"

        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            size_kb = size / 1024
            result += f" - {log_file.name} ({size_kb:.2f} KB)\n"

        return result

    except Exception as e:
        return f"Error: An unexpected error occurred while listing log files: {str(e)}"


@tool
def search_logs(filename: str, search_term: str) -> str:
    """
    Search for a specific term in a log file.
    Input: filename (str): The name of the log file to search.
           search_term (str): The term to search for in the log file.

    Return: String containing the lines with line numbers.
    """
    log_path = os.path.join(Config.LOG_DIRECTORY, filename)

    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Search for the term in the lines
        matches = []
        for line_num, line in enumerate(lines, start=1):
            if search_term.lower() in line.lower():
                matches.append(f"Line {line_num}: {line.strip()}")

        if not matches:
            return f"No matches found for '{search_term}' in log file '{filename}'."
        
        result = f"Found {len(matches)} matches for '{search_term}' in log file '{filename}':\n"
        result += "\n".join(matches)
        return result
    except FileNotFoundError:
        return f"Error: Log file '{filename}' not found in directory '{Config.LOG_DIRECTORY}'."

    except Exception as e:
        return f"Error: An unexpected error occurred while searching log file '{filename}': {str(e)}"