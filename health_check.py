import time
import subprocess
import os
import datetime

# These are the techniques to monitor continuously
TECHNIQUES = ["registry_run_key", "winlogon_shell", "dll_hijack_iexplore", "admin_service_persistence", "admin_wmi_persistence", "scheduled_task"]

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
        if technique == "registry_run_key":
            # Checks HKCU Run Key
            proc = subprocess.run(["python", "sentinel_monitors/check_registry_run_key.py"])
            return proc.returncode == 0

        elif technique == "winlogon_shell":
            # Checks HKLM Winlogon Shell
            proc = subprocess.run(["python", "sentinel_monitors/check_winlogon_shell.py"])
            return proc.returncode == 0

        elif technique == "dll_hijack_iexplore":
            # Checks for suspend.dll in IE folder
            proc = subprocess.run(["python", "sentinel_monitors/check_dll_hijack_iexplore.py"])
            return proc.returncode == 0

        elif technique == "admin_service_persistence":
            # Checks if the Service is registered and running
            proc = subprocess.run(["python", "sentinel_monitors/check_admin_service_persistence.py"])
            return proc.returncode == 0

        elif technique == "admin_wmi_persistence":
            # Call the MONITOR script, not the installer!
            proc = subprocess.run(["python", "sentinel_monitors/check_admin_wmi_persistence.py"])
            return proc.returncode == 0
        
        elif technique == "scheduled_task":
            proc = subprocess.run(["python", "sentinel_monitors/check_scheduled_task.py"])
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
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[*] Exiting Sentinel-agent. Goodbye!")