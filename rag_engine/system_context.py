"""
system_context.py
-----------------
Collects live system metadata to enrich the LLM prompt payload:
  - Current privilege level  (Admin / User)
  - Windows OS build string  (e.g. "Windows 10 Build 19045")
  - Registered AV / EDR products from the Windows Security Center WMI namespace

All collection is done with stdlib modules only (ctypes, platform, subprocess).
If any query fails, it degrades gracefully with a descriptive fallback string.
"""

import ctypes
import platform
import subprocess
import json


# ---------------------------------------------------------------------------
# 1. Privilege Level
# ---------------------------------------------------------------------------

def get_privilege_level() -> str:
    """
    Returns 'Admin' if the current process has elevated (administrator) privileges,
    otherwise 'User'.
    Uses ctypes.windll.shell32.IsUserAnAdmin() which is the canonical Windows check.
    """
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return "Admin" if is_admin else "User"
    except Exception:
        return "Unknown"


# ---------------------------------------------------------------------------
# 2. OS Build
# ---------------------------------------------------------------------------

def get_os_build() -> str:
    """
    Returns a human-readable OS build string.
    Example: "Windows 10 Build 19045.4412"
    Uses platform.version() for the full build number and platform.win32_ver()
    for the marketing release (e.g. "10", "11").
    """
    try:
        # win32_ver() -> (release, version, csd, ptype)
        # release: '10', '11', etc.  |  version: '10.0.19045' etc.
        release, version, _, _ = platform.win32_ver()

        # Extract just the build number (3rd field of the dotted version string)
        parts = version.split(".")
        build = parts[2] if len(parts) >= 3 else version

        # Attempt to get the UBR (Update Build Revision) from the registry for precision
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion').UBR"],
                capture_output=True, text=True, timeout=5
            )
            ubr = result.stdout.strip()
            if ubr.isdigit():
                build = f"{build}.{ubr}"
        except Exception:
            pass  # UBR is a nice-to-have; skip if unavailable

        return f"Windows {release} Build {build}"
    except Exception as e:
        return f"Unknown (error: {e})"


# ---------------------------------------------------------------------------
# 3. AV / EDR Status
# ---------------------------------------------------------------------------

def get_av_edr_status() -> list:
    """
    Queries the Windows Security Center (WSC) WMI namespace for all registered
    AV products and returns a list of dicts, each with:
      - 'name':   display name of the product
      - 'state':  decoded state string (e.g. "Enabled, Up-to-date")

    The productState field is a packed DWORD. Relevant bit-field layout:
      Bits 12-15 : AV product enabled  (0x1000 = ON, 0x0000 = OFF)
      Bits 4-7   : Signature up-to-date (0x00 = OK, 0x10 = OUT-OF-DATE)

    Falls back to Windows Defender status via Get-MpComputerStatus if WSC query fails.
    """
    ps_command = (
        "Get-CimInstance -Namespace 'root/SecurityCenter2' -ClassName 'AntiVirusProduct' "
        "| Select-Object displayName, productState "
        "| ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True, text=True, timeout=10
        )
        raw = result.stdout.strip()
        if not raw:
            raise ValueError("Empty output from SecurityCenter2 query")

        # PowerShell may return a single object (dict) or an array of objects
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed = [parsed]

        av_list = []
        for entry in parsed:
            name = entry.get("displayName", "Unknown")
            state_code = entry.get("productState", 0)

            # Decode the packed DWORD state
            enabled = (state_code >> 12) & 0xF  # 1 = enabled, 0 = disabled
            updated = (state_code >> 4) & 0xFF  # 0 = up-to-date, non-zero = out of date

            status_str = "Enabled" if enabled == 1 else "Disabled"
            sig_str    = "Up-to-date" if updated == 0 else "Out-of-date"

            av_list.append({
                "name":  name,
                "state": f"{status_str}, {sig_str}"
            })

        return av_list if av_list else [{"name": "None detected", "state": "N/A"}]

    except Exception:
        # Fallback: query Windows Defender directly via Get-MpComputerStatus
        return _get_defender_fallback()


def _get_defender_fallback() -> list:
    """
    Fallback AV check using Windows Defender's Get-MpComputerStatus cmdlet.
    Returns a minimal status dict if Defender is present.
    """
    ps_command = (
        "Get-MpComputerStatus "
        "| Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureAge "
        "| ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True, text=True, timeout=10
        )
        raw = result.stdout.strip()
        if not raw:
            return [{"name": "Unknown", "state": "Query failed"}]

        data = json.loads(raw)
        av_on  = data.get("AntivirusEnabled", False)
        rtp_on = data.get("RealTimeProtectionEnabled", False)
        sig_age = data.get("AntivirusSignatureAge", "?")

        state = f"{'Enabled' if av_on else 'Disabled'}, RTP={'On' if rtp_on else 'Off'}, SigAge={sig_age}d"
        return [{"name": "Windows Defender", "state": state}]
    except Exception as e:
        return [{"name": "Unknown", "state": f"Query failed: {e}"}]


# ---------------------------------------------------------------------------
# 4. Public API — single call to get everything
# ---------------------------------------------------------------------------

def collect() -> dict:
    """
    Returns a single dict containing all system context metadata:
      {
          "privilege_level": "Admin" | "User" | "Unknown",
          "os_build":        "Windows 10 Build 19045.4412",
          "av_edr_status":   [{"name": "...", "state": "..."}, ...]
      }
    """
    return {
        "privilege_level": get_privilege_level(),
        "os_build":        get_os_build(),
        "av_edr_status":   get_av_edr_status(),
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ctx = collect()
    print(f"[+] Privilege Level : {ctx['privilege_level']}")
    print(f"[+] OS Build        : {ctx['os_build']}")
    print(f"[+] AV / EDR Status :")
    for av in ctx["av_edr_status"]:
        print(f"      - {av['name']} -> {av['state']}")
