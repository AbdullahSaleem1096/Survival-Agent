import winreg
import sys

def check_winlogon_shell():
    path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    value_name = "Shell"
    
    try:
        # Open HKLM (Local Machine) - Requires matching permissions
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
        value, reg_type = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        # This value should be "explorer.exe,C:\path\to\agent.exe"
        if "agent.exe" in value and "explorer.exe" in value:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    check_winlogon_shell()