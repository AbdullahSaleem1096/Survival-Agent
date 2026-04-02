#include <windows.h>

// This is the entry point for a DLL
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            // This code runs when the DLL is loaded into a process
            MessageBoxA(NULL, "Hello, Packt! (From DLL)", "=^..^=", MB_OK);
            break;

        case DLL_PROCESS_DETACH:
            // This runs when the DLL is unloaded
            break;
    }
    return TRUE; // Successful DLL_PROCESS_ATTACH
}

// run this command to compile the code
// x86_64-w64-mingw32-g++ -shared -o dll_hijacking.dll dll_hijacking.c
