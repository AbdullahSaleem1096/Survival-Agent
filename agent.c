#include <windows.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    MessageBoxA(NULL, "Hello, Packt!", "=^..^=", MB_OK);
    return 0;
}

// use this command to make the executable of agent.c
// x86_64-w64-mingw32-g++ -O2 agent.c -o agent.exe -mwindows