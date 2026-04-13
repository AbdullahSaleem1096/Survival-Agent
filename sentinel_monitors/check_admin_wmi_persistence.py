import subprocess
import sys

def check_wmi_persistence():
    name = "WindowsHealthCheck"
    
    cmd = f"[bool](Get-WmiObject -Namespace root\\subscription -Class __EventFilter -Filter \"Name='{name}'\")"
    
    try:
        proc = subprocess.run(["powershell.exe", "-Command", cmd], capture_output=True, text=True)
        
        # Strip trailing newlines and whitespace
        out = proc.stdout.strip()
        
        if out == "True":
            sys.exit(0) # HEALTHY
        else:
            sys.exit(1) # DELETED
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    check_wmi_persistence()