from .log_reader import list_log_files, read_log_file, search_logs
from .k8s_action import restart_kubernetes_pod


def get_log_tools():
    return [list_log_files, read_log_file, search_logs, restart_kubernetes_pod]
