import winreg
import sys

def check_run_key():
    path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    value_name = "SurvivalAgent"
    
    try:
        # Open HKCU (Current User)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ)
        # Check if the specific value name exists
        value, reg_type = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        # If it exists and points to our agent, it's Healthy
        if "agent.exe" in value:
            sys.exit(0) 
        else:
            sys.exit(1)
    except Exception:
        sys.exit(1) # Key or Value was deleted

if __name__ == "__main__":
    check_run_key()