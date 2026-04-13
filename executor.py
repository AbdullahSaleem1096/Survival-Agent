import os
import subprocess

def deploy_technique(cpp_filename: str) -> bool:
    """
    Takes a .cpp filename as input.
    Uses subprocess to compile it using x86_64-w64-mingw32-g++.
    Executes the resulting .exe.
    """
    # Check if the file exists in the current directory or knowledge_library/
    if not os.path.exists(cpp_filename):
        lib_path = os.path.join("knowledge_library", cpp_filename)
        if os.path.exists(lib_path):
            cpp_filename = lib_path
        else:
            print(f"[-] Source file not found: {cpp_filename}")
            return False

    base_name = os.path.splitext(os.path.basename(cpp_filename))[0]
    exe_filename = f"{base_name}.exe"
    
    print(f"[*] Compiling {cpp_filename} -> {exe_filename}...")
    compile_cmd = ["x86_64-w64-mingw32-g++", cpp_filename, "-o", exe_filename]
    
    try:
        # Compile the C++ file
        compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)
        if compile_proc.returncode != 0:
            print(f"[-] Compilation failed:\n{compile_proc.stderr}")
            return False
            
        print(f"[+] Compilation successful.")
        print(f"[*] Executing {exe_filename}...")
        
        # Execute the resulting .exe
        exec_proc = subprocess.run([f".\\{exe_filename}"], capture_output=True, text=True)
        
        print(f"[+] Execution completed with return code: {exec_proc.returncode}")
        if exec_proc.stdout:
            print(f"[*] Output:\n{exec_proc.stdout}")
        if exec_proc.stderr:
            print(f"[-] Error Output:\n{exec_proc.stderr}")
            
        return True
            
    except Exception as e:
        print(f"[-] Error during compilation or execution: {e}")
        return False

def verify_deployment(technique_name: str) -> bool:
    """
    Calls the corresponding script in sentinel_monitors/ folder and returns a Boolean.
    """
    technique_name_lower = technique_name.lower()
    monitor_script = None
    
    # Map technique to monitor script dynamically
    if "run_key" in technique_name_lower:
        monitor_script = "sentinel_monitors/check_registry_run_key.py"
    elif "winlogon" in technique_name_lower:
        monitor_script = "sentinel_monitors/check_winlogon_shell.py"
    elif "dll" in technique_name_lower:
        monitor_script = "sentinel_monitors/check_dll_hijack_iexplore.py"
    elif "service" in technique_name_lower:
        monitor_script = "sentinel_monitors/check_admin_service_persistence.py"
    elif "wmi" in technique_name_lower:
        monitor_script = "sentinel_monitors/check_admin_wmi_persistence.py"
    elif "task" in technique_name_lower:
        monitor_script = "sentinel_monitors/check_deploy_task.py"
    else:
        # Exact match attempts for previously listed names
        script_map = {
            "registry_run_key": "sentinel_monitors/check_registry_run_key.py",
            "winlogon_shell": "sentinel_monitors/check_winlogon_shell.py",
            "dll_hijack_iexplore": "sentinel_monitors/check_dll_hijack_iexplore.py",
            "admin_service_persistence": "sentinel_monitors/check_admin_service_persistence.py",
            "admin_wmi_persistence": "sentinel_monitors/check_admin_wmi_persistence.py",
            "deploy_task": "sentinel_monitors/check_deploy_task.py"
        }
        monitor_script = script_map.get(technique_name_lower)
        
    if not monitor_script:
        print(f"[-] Monitor mapping for '{technique_name}' not found.")
        return False
        
    # Make sure we can find the script
    monitor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), monitor_script)
    if not os.path.exists(monitor_path):
         if os.path.exists(monitor_script):
             monitor_path = monitor_script
         else:
             print(f"[-] Monitor script not found at {monitor_path}")
             return False
        
    print(f"[*] Verifying deployment using {monitor_script}...")
    try:
        proc = subprocess.run(["python", monitor_path], capture_output=True, text=True)
        if proc.returncode == 0:
            print(f"[+] Verification passed for {technique_name}!")
            return True
        else:
            print(f"[-] Verification failed for {technique_name}.")
            return False
    except Exception as e:
        print(f"[-] Verification script execution error: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        tech_file = sys.argv[1]
        success = deploy_technique(tech_file)
        if success:
            verify_deployment(tech_file)
    else:
        print("Usage: python executor.py <technique_file.cpp>")
    
    print(verify_deployment("admin_wmi_persistence.cpp"))
