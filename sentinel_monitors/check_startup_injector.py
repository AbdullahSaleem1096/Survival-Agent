import os
import sys

def check_startup_health():
    # Path to the current user's startup folder
    startup_dir = os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs\Startup")
    target_lnk = os.path.join(startup_dir, "OneDriveUpdateHelper.lnk")

    if os.path.exists(target_lnk):
        sys.exit(0)  # HEALTHY
    else:
        sys.exit(1)  # TAMPERED/DELETED

if __name__ == "__main__":
    check_startup_health()