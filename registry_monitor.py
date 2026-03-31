import winreg
import time
import datetime
import platform
import ctypes
import os

# Configuration: Update these variables to monitor a different key
HIVE = winreg.HKEY_CURRENT_USER
KEY_PATH = r"Software\MyMonitoredApp"  # Example path
LOG_FILE = "recovery_events.log"

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_system_metadata():
    """Retrieve OS version and user privileges."""
    os_version = platform.platform()
    privileges = "Administrator elevated privileges" if is_admin() else "Standard User privileges"
    return os_version, privileges

def log_recovery_event():
    """Log the recovery event when the monitored registry key is deleted."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_version, privileges = get_system_metadata()
    
    log_entry = (
        f"[{timestamp}] RECOVERY EVENT\n"
        f"Description: Monitored registry key was deleted.\n"
        f"Registry Path: {KEY_PATH}\n"
        f"OS System: {os_version}\n"
        f"User Context: {privileges}\n"
        f"{'-'*50}\n"
    )
    
    try:
        # Save to the same directory as the script
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILE)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{timestamp}] Recovery event logged successfully.")
    except Exception as e:
        print(f"[{timestamp}] Error writing to log file: {e}")

def monitor_registry():
    """Monitor the registry key and trigger logging if deleted."""
    print(f"Starting registry monitor for: {KEY_PATH}")
    print("Checking every 30 seconds... (Press Ctrl+C to stop)")
    
    # Track the state to avoid continuous logging if it stays deleted
    key_exists = False
    
    # Initial state check
    try:
        with winreg.OpenKey(HIVE, KEY_PATH, 0, winreg.KEY_READ):
            key_exists = True
            print("Initial state: Key exists.")
    except FileNotFoundError:
        print("Initial state: Key does not exist currently.")
    except PermissionError:
         print("Initial state: Access Denied. Ensure you have the required permissions.")
         return
    except Exception as e:
        print(f"Error accessing key at startup: {e}")
        return

    while True:
        try:
            # Attempt to open the key
            with winreg.OpenKey(HIVE, KEY_PATH, 0, winreg.KEY_READ):
                if not key_exists:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Key found (created/restored).")
                    key_exists = True
        except FileNotFoundError:
            if key_exists:
                # Key existed in the last check but is missing now
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Key deletion detected!")
                log_recovery_event()
                key_exists = False # Update state so we don't spam the log
        except Exception as e:
             print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Unexpected error: {e}")
            
        time.sleep(30) # Wait 30 seconds before the next check

if __name__ == "__main__":
    try:
        monitor_registry()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
