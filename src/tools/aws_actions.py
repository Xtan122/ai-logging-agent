from langchain.tools import tool
import os

def _is_aws_configured() -> bool:
    """Check if AWS credentials are configured"""
    return bool(os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY') and os.getenv('AWS_SESSION_TOKEN'))

@tool
def reboot_rds_instance(db_instance_id: str, reason: str = "") -> str:
    """
    Reboot an AWS RDS database instance to reset connections and restore service.

    IMPORTANT: Always ask for user approval before using this tool. 
    This will cause a brief service interruption (typically 1-3 minutes for a reboot).
    Use this when logs show "Too many connections" errors across multiple
    application pods,
    indicating the RDS instance has exhausted its connection limit.
    
    Args:
        db_instance_id: The RDS instance identifier (e.g., 'orders-db-prod')
        reason: Reason for the reboot (e.g., 'Connection pool exhaustion recovery')
    """
    if _is_aws_configured():
        return _reboot_rds_real(db_instance_id, reason)
    else:
        return _reboot_rds_placeholder(db_instance_id, reason)


def _reboot_rds_real(db_instance_id: str, reason: str) -> str:
    """Real AWS RDS reboot using boto3"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        region = os.getenv('AWS_REGION', 'us-east-1')
        rds_client = boto3.client('rds', region_name=region)
        # Check instance status before rebooting
        response = rds_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )
        instance = response['DBInstances'][0]
        status = instance['DBInstanceStatus']
        
        if status != "available":
            return (f"Cannot reboot RDS Instance {db_instance_id}: "
                f"currently in '{status}' state. "
                f"Please wait for it to become 'available' and try again."
            )
        # Perform the reboot
        rds_client.reboot_db_instance(
            DBInstanceIdentifier=db_instance_id
        )
        
        return (f"Successfully initiated reboot for RDS instance '{db_instance_id}'. "
                f"in region {region}."
                f"With reason {reason}."
                f"The instance will restart automatically. "
                f"Please check its status in 1-2 minutes.")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'DBInstanceNotFound':
            return f"Cannot reboot RDS instance: {db_instance_id} not found."
        
def _reboot_rds_placeholder(db_instance_id: str, reason: str) -> str:
    """Placeholder for RDS reboot (used when AWS not configured)"""
    sep = "=" * 80
    print(f"\n{sep}")
    print(f"SIMULATED ACTION: Rebooting AWS RDS Instance")
    print(sep)
    print(f"1. RDS Instance:   {db_instance_id}")
    print(f"2. Region:         us-east-1 (default)")
    print(f"3. Reason:         {reason}")
    print(f"4. Action:         Rebooting RDS instance '{db_instance_id}'")
    print(f"5. Expected:       Database connection pool will reset, restoring service.")
    print(sep + "\n")
    
    return (
        f"[SIMULATED] Successfully initiated reboot for RDS instance '{db_instance_id}'.\n"
        f"'{db_instance_id}' is in region '{region}'."
        f"With reason {reason}."
        f"[SIMULATED] The instance will restart automatically.\n"
        f"[SIMULATED] Please check its status in 1-2 minutes."
    )