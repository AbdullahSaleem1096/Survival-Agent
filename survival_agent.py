import time
import subprocess
import os
import datetime

# These are the techniques to monitor continuously
TECHNIQUES = ["run_key", "winlogon", "dll_hijack", "windows_service","wmi_event","scheduled_task"]

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("survival_log.txt", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def check_health(technique):
    """
    Executes the specific monitor for the given technique.
    Returns True if healthy, False if deleted/broken.
    """
    try:
        if technique == "run_key":
            # Checks HKCU Run Key
            proc = subprocess.run(["python", "sentinel_monitors/check_run_key.py"])
            return proc.returncode == 0

        elif technique == "winlogon":
            # Checks HKLM Winlogon Shell
            proc = subprocess.run(["python", "sentinel_monitors/check_winlogon.py"])
            return proc.returncode == 0

        elif technique == "dll_hijack":
            # Checks for suspend.dll in IE folder
            proc = subprocess.run(["python", "sentinel_monitors/check_dll.py"])
            return proc.returncode == 0

        elif technique == "windows_service":
            # Checks if the Service is registered and running
            proc = subprocess.run(["python", "sentinel_monitors/check_service.py"])
            return proc.returncode == 0

        elif technique == "wmi_event":
            # Call the MONITOR script, not the installer!
            proc = subprocess.run(["python", "sentinel_monitors/check_wmi.py"])
            return proc.returncode == 0
        
        elif technique == "scheduled_task":
            proc = subprocess.run(["python", "sentinel_monitors/check_task.py"])
            return proc.returncode == 0

    except Exception as e:
        print(f"[-] Monitor Error: {e}")
        return False
    
    return False

def main_loop():
    print(f"[*] Sentinel started. Monitoring techniques: {', '.join(TECHNIQUES)}")
    log_event(f"Monitoring started for techniques: {', '.join(TECHNIQUES)}")
    
    while True:
        for technique in TECHNIQUES:
            is_healthy = check_health(technique)
            
            if not is_healthy:
                print(f"[!] RECOVERY EVENT TRIGGERED: {technique} has been compromised!")
                log_event(f"FAILURE DETECTED: {technique} removed by system/user.")
                
                # --- NEXT PHASE (Requirement D) ---
                # 1. Add technique to a 'blacklist'
                # 2. Ask Dolphin LLM for a new technique from Knowledge Library
                # 3. Execute the new .exe or .ps1
            else:
                print(f"[+] {datetime.datetime.now().strftime('%H:%M:%S')} - Health Check ({technique}): OK")
                log_event(f"HEALTH OK: {technique} is active and running.")
                
        time.sleep(30) # 30-second interval per Requirement A
        print("\n")

if __name__ == "__main__":
    main_loop()