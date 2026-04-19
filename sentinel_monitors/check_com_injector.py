import winreg
import os
import sys

def check_com_persistence():
    # The target SmartScreen CLSID
    clsid = "{a463fcb9-6b1c-4e0d-a80b-a2ca7999e25d}"
    reg_path = f"Software\\Classes\\CLSID\\{clsid}\\InProcServer32"
    
    # Path to your expected malicious DLL
    expected_dll = r"C:\Users\abdul\Downloads\FYP\Survival-Agent\com_hijacking.dll"

    try:
        # Open the key in the CURRENT_USER hive
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
        
        # Read the (Default) value
        current_dll, _ = winreg.QueryValueEx(key, None)
        winreg.CloseKey(key)

        # Check if the path matches and the file actually exists
        if current_dll.lower() == expected_dll.lower() and os.path.exists(expected_dll):
            # Status: HEALTHY
            sys.exit(0)
        else:
            # Status: TAMPERED (Path mismatch or file deleted)
            sys.exit(1)

    except FileNotFoundError:
        # Status: DELETED (Registry key is missing)
        sys.exit(1)
    except Exception:
        # Status: ERROR (Possible permission block)
        sys.exit(1)

if __name__ == "__main__":
    check_com_persistence()