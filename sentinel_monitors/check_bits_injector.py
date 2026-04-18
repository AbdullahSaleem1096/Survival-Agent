import subprocess
import sys
import os
import tempfile
import ctypes

def is_admin():
    """Check if the current process has admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def check_bits_health():
    job_name = "SurvivalTask"

    # --- Strategy 1: Direct bitsadmin (works if already running as admin) ---
    for flags in [['bitsadmin', '/list', '/allusers'], ['bitsadmin', '/list']]:
        try:
            result = subprocess.run(flags, capture_output=True, text=True, timeout=10)
            combined = result.stdout + result.stderr
            if job_name.lower() in combined.lower():
                return True  # Job found
            # If /allusers succeeded (no "Access is denied") but job not found, it's genuinely absent
            if flags[-1] == '/allusers' and 'access is denied' not in combined.lower():
                return False
        except Exception:
            continue

    # --- Strategy 2: Elevated PowerShell via temp file (when running non-elevated) ---
    # Write bitsadmin output to a temp file via an elevated powershell process
    tmp_out = os.path.join(tempfile.gettempdir(), "bits_check_out.txt")
    try:
        # Build a PS command that runs bitsadmin elevated and saves output
        ps_cmd = (
            f"bitsadmin /list /allusers 2>&1 | Out-File -FilePath '{tmp_out}' -Encoding utf8 -Force"
        )
        # Start-Process with -Verb RunAs triggers UAC, -Wait ensures we block
        subprocess.run(
            [
                "powershell", "-ExecutionPolicy", "Bypass", "-Command",
                f"Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -Command \"{ps_cmd}\"' -Verb RunAs -Wait -WindowStyle Hidden"
            ],
            timeout=30,
            capture_output=True
        )
        if os.path.exists(tmp_out):
            with open(tmp_out, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            os.remove(tmp_out)
            if job_name.lower() in content.lower():
                return True
            # If output is non-empty and has no access denied, job genuinely absent
            if content.strip() and 'access is denied' not in content.lower():
                return False
    except Exception:
        pass

    # Cannot determine status — treat as absent to trigger recovery
    return False

if __name__ == "__main__":
    if check_bits_health():
        sys.exit(0)  # Exit code 0 — job exists, persistence healthy
    else:
        sys.exit(1)  # Exit code 1 — job missing, triggers recovery