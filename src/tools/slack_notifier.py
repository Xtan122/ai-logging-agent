from langchain.tools import tool
from src.config import Config

@tool
def send_slack_notification(
    channel: str,
    summary: str,
    severity: str = "P1",
    details: str = "",
    actions_taken: str = ""
) -> str:
    """
    Send an incident notification to a Slack channel with details about
    the issue and actions taken.
    Args:
        channel: Slack channel name (e.g., '#devops-alerts')
        summary: Brief incident summary
        severity: Incident severity level ('P1', 'P2', 'P3', 'info')
        details: Detailed description of the issue and root cause
        actions_taken: Description of remediation actions that were executed
    """

    if _is_slack_configured():
        return _send_slack_real(channel, summary, severity, details, actions_taken)
    else:
        return _send_slack_placeholder(channel, summary, severity, details, actions_taken)