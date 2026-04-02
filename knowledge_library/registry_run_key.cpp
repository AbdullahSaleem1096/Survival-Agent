/* Technique: Classic Registry Run Key Persistence
Privilege Level: User (HKCU)
Description: Adds an entry to the current user's Run key to execute on login.
*/
#include <windows.h>
#include <string.h>

int main() {
    HKEY hkey = NULL;
    // Path to your survival agent executable
    const char* exe = "C:\\Users\\abdul\\Downloads\\FYP\\task1\\agent.exe";

    // Open the Run key for the current user
    LONG result = RegOpenKeyEx(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_WRITE, &hkey);
    
    if (result == ERROR_SUCCESS) {
        // Create a value named "SurvivalAgent" pointing to the exe
        RegSetValueEx(hkey, "SurvivalAgent", 0, REG_SZ, (unsigned char*)exe, strlen(exe));
        RegCloseKey(hkey);
    }
    return 0;
}

// run this command to compile the code
// x86_64-w64-mingw32-g++ registry_run_key.cpp -o registry_run_key.exe