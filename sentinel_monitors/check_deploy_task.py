import subprocess
import sys

def check_task_exists():
    task_name = "MyScheduledTask"
    # Use schtasks.exe to query the task
    cmd = ["schtasks", "/Query", "/TN", task_name]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if task_name in result.stdout:
            sys.exit(0) # HEALTHY
        else:
            sys.exit(1) # DELETED
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    check_task_exists()