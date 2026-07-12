from .log_reader import list_log_files, read_log_file, search_logs


def get_log_tools():
    return [list_log_files, read_log_file, search_logs]
