#include <windows.h>
#include <taskschd.h>
#include <comdef.h>
#include <stdio.h>

#pragma comment(lib, "taskschd.lib")
#pragma comment(lib, "comsupp.lib")

int main() {
    HRESULT hr;

    // Initialize COM
    hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
    if (FAILED(hr)) {
        printf("Failed to initialize COM: 0x%x\n", hr);
        return 1;
    }

    // Set general COM security levels
    hr = CoInitializeSecurity(
        NULL,
        -1,
        NULL,
        NULL,
        RPC_C_AUTHN_LEVEL_PKT_PRIVACY,
        RPC_C_IMP_LEVEL_IMPERSONATE,
        NULL,
        0,
        NULL
    );

    // Create Task Service
    ITaskService *pService = NULL;
    hr = CoCreateInstance(CLSID_TaskScheduler, NULL, CLSCTX_INPROC_SERVER,
                          IID_ITaskService, (void**)&pService);

    if (FAILED(hr)) {
        printf("Failed to create Task Service: 0x%x\n", hr);
        CoUninitialize();
        return 1;
    }

    // Connect to Task Scheduler
    hr = pService->Connect(_variant_t(), _variant_t(),
                           _variant_t(), _variant_t());

    if (FAILED(hr)) {
        printf("Failed to connect: 0x%x\n", hr);
        pService->Release();
        CoUninitialize();
        return 1;
    }

    // Get root folder
    ITaskFolder *pRootFolder = NULL;
    hr = pService->GetFolder(_bstr_t(L"\\"), &pRootFolder);

    // Create task definition
    ITaskDefinition *pTask = NULL;
    hr = pService->NewTask(0, &pTask);

    // -------------------------
    // SET TRIGGER (REAL WAY)
    // -------------------------
    ITriggerCollection *pTriggerCollection = NULL;
    pTask->get_Triggers(&pTriggerCollection);

    ITrigger *pTrigger = NULL;
    pTriggerCollection->Create(TASK_TRIGGER_TIME, &pTrigger);

    ITimeTrigger *pTimeTrigger = NULL;
    pTrigger->QueryInterface(IID_ITimeTrigger, (void**)&pTimeTrigger);

    // Start time
    pTimeTrigger->put_StartBoundary(_bstr_t(L"2026-04-09T12:00:00"));

    // Repeat every 5 minutes
    IRepetitionPattern *pRepetition = NULL;
    pTimeTrigger->get_Repetition(&pRepetition);
    pRepetition->put_Interval(_bstr_t(L"PT5M")); // every 5 min
    pRepetition->put_Duration(_bstr_t(L"P1D")); // repeat for 1 day

    // -------------------------
    // SET ACTION (WHAT TO RUN)
    // -------------------------
    IActionCollection *pActionCollection = NULL;
    pTask->get_Actions(&pActionCollection);

    IAction *pAction = NULL;
    pActionCollection->Create(TASK_ACTION_EXEC, &pAction);

    IExecAction *pExecAction = NULL;
    pAction->QueryInterface(IID_IExecAction, (void**)&pExecAction);

    //pExecAction->put_Path(_bstr_t(L"C:\\Windows\\System32\\notepad.exe"));
    pExecAction->put_Path(_bstr_t(L"C:\\Users\\abdul\\Downloads\\FYP\\task1\\agent.exe"));
    // -------------------------
    // REGISTER TASK
    // -------------------------
    IRegisteredTask *pRegisteredTask = NULL;

    hr = pRootFolder->RegisterTaskDefinition(
        _bstr_t(L"MyScheduledTask"),
        pTask,
        TASK_CREATE_OR_UPDATE,
        _variant_t(),
        _variant_t(),
        TASK_LOGON_INTERACTIVE_TOKEN,
        _variant_t(L""),
        &pRegisteredTask
    );

    if (SUCCEEDED(hr)) {
        printf("Task created successfully!\n");
    } else {
        printf("Failed to register task: 0x%x\n", hr);
    }

    // Cleanup
    if (pRegisteredTask) pRegisteredTask->Release();
    if (pRootFolder) pRootFolder->Release();
    if (pService) pService->Release();

    CoUninitialize();
    return 0;
}