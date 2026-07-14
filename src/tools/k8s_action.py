from langchain.tools import tool
from ..config import Config

@tool
def restart_kubernetes_pod(
    pod_name: str,
    namespace: str = "default",
    reason: str = ""
) -> str:
    """
    Restart a Kubernetes pod by deleting it.
    The pod will be automatically recreated by the deployment.

    Args:
        pod_name: Name of the pod to restart
        namespace: Namespace of the pod
        reason: Reason for restarting the pod

    Returns:
        Success or Error message
    """
    sep = "=" * 80
    print(f"\n{sep}")
    print(f"SIMULATED ACTION: Restarting Kubernetes Pod")
    print(sep)
    print(f"1. Pod Name:    {pod_name}")
    print(f"2. Namespace:   {namespace}")
    print(f"3. Reason:      {reason}")
    print(f"4. Action:      Deleting pod '{pod_name}' in namespace '{namespace}'")
    print(f"5. Expected:    Pod will be recreated automatically by the deployment.")
    print(f"{sep}\n")

    return (
        f"[SIMULATED] Successfully deleted pod '{pod_name}' in namespace '{namespace}'.\n"
        f"[SIMULATED] The pod will be recreated automatically by the deployment."
    )


