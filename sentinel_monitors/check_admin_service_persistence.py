import subprocess
import sys

def check_service_status():
    service_name = "WindowsUpdateAssist" # The name used in your PS1 script
    
    try:
        # Run 'sc query' to check the service
        result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True)
        
        # If the service name isn't in the output, it was deleted
        if f"SERVICE_NAME: {service_name}" in result.stdout:
            # Check if it is actually RUNNING
            if "STATE" in result.stdout and "RUNNING" in result.stdout:
                sys.exit(0) # HEALTHY
            else:
                sys.exit(1) # STOPPED (still a failure for persistence)
        else:
            sys.exit(1) # DELETED
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    check_service_status()