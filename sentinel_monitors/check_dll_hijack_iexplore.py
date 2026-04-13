import os
import sys

def check_dll_exists():
    # The path to the 'suspend.dll' we hijacked
    dll_path = r"C:\Program Files\Internet Explorer\suspend.dll"
    
    if os.path.exists(dll_path):
        sys.exit(0) # HEALTHY
    else:
        sys.exit(1) # DELETED
        
if __name__ == "__main__":
    check_dll_exists()