import winreg
import sys

def check_ifeo_health():
    # Target Registry Path
    path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe"
    target_agent = "agent.exe"

    try:
        # Open the key for reading
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        
        # Check both the Debugger path and the Filter status
        debugger_val, _ = winreg.QueryValueEx(key, "Debugger")
        filter_val, _ = winreg.QueryValueEx(key, "UseFilter")
        
        # If the agent is missing or the filter is re-enabled (1), it's a failure
        if target_agent.lower() in debugger_val.lower() and filter_val == 0:
            sys.exit(0)  # HEALTHY
        else:
            sys.exit(1)  # TAMPERED
            
    except (FileNotFoundError, OSError):
        sys.exit(1)  # DELETED

if __name__ == "__main__":
    check_ifeo_health()