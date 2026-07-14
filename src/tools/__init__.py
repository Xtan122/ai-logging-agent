from .log_reader import list_log_files, read_log_file, search_logs
from .actions import restart_kubernetes_pod
from .aws_actions import reboot_rds_instance
from .slack_notifier import send_slack_notification


SAFE_TOOLS = {'read_log_file', 'list_log_files', 'search_logs', 'send_slack_notification'}
APPROVAL_REQUIRED_TOOLS = {'reboot_rds_instance', 'restart_kubernetes_pod'}

def requires_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS

def get_log_tools():
    """Return all tools available to the agent."""
    return [
        list_log_files,
        read_log_file,
        search_logs,
        send_slack_notification,
        restart_kubernetes_pod,
        reboot_rds_instance,
    ]