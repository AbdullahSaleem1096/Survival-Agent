import os
import datetime
try:
    from system_context import collect
except ImportError:
    try:
        from rag_engine.system_context import collect
    except ImportError:
        collect = None

def log_event(message, include_state=False):
    """
    Centralized logging function for the Survival Agent.
    Logs to survival_log.txt in the project root.
    """
    # Determine the project root (where survival_log.txt lives)
    # This assumes logger_util.py is in rag_engine/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    log_path = os.path.join(project_root, "survival_log.txt")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    if include_state and collect:
        try:
            state = collect()
            log_entry += "[SYSTEM STATE AT FAILURE]\n"
            log_entry += f"- Privilege Level: {state.get('privilege_level', 'Unknown')}\n"
            log_entry += f"- OS Build: {state.get('os_build', 'Unknown')}\n"
            log_entry += "- AV / EDR Status:\n"
            for av in state.get('av_edr_status', []):
                log_entry += f"    * {av.get('name', 'Unknown')} -> {av.get('state', 'N/A')}\n"
            log_entry += "-" * 50 + "\n"
        except Exception as e:
            log_entry += f"[!] Error capturing system state: {e}\n"
    
    try:
        with open(log_path, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[-] Logger Error: Failed to write to {log_path}. {e}")
