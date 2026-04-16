#define _WIN32_DCOM
#include <iostream>
#include <comdef.h>
#include <Wbemidl.h>

// For MSVC; with mingw you might instead link via -lole32 -loleaut32 -lwbemuuid
#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")

int main() {
    HRESULT hres;

    hres = CoInitializeEx(0, COINIT_MULTITHREADED); 
    if (FAILED(hres)) return 1;

    hres = CoInitializeSecurity(
        NULL, -1, NULL, NULL,
        RPC_C_AUTHN_LEVEL_DEFAULT,
        RPC_C_IMP_LEVEL_IMPERSONATE,
        NULL, EOAC_NONE, NULL
    );
    if (FAILED(hres)) { CoUninitialize(); return 1; }

    IWbemLocator* pLoc = NULL;
    hres = CoCreateInstance(CLSID_WbemLocator, 0, CLSCTX_INPROC_SERVER, IID_IWbemLocator, (LPVOID*)&pLoc);
    if (FAILED(hres)) { CoUninitialize(); return 1; }

    IWbemServices* pSvc = NULL;
    hres = pLoc->ConnectServer(_bstr_t(L"ROOT\\subscription"), NULL, NULL, NULL, 0, NULL, NULL, &pSvc);
    if (FAILED(hres)) { pLoc->Release(); CoUninitialize(); return 1; }

    hres = CoSetProxyBlanket(
        pSvc, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE, NULL,
        RPC_C_AUTHN_LEVEL_CALL, RPC_C_IMP_LEVEL_IMPERSONATE, NULL, EOAC_NONE
    );

    // 1. Filter
    IWbemClassObject* pFilterClass = NULL;
    hres = pSvc->GetObject(_bstr_t(L"__EventFilter"), 0, NULL, &pFilterClass, NULL);
    
    IWbemClassObject* pFilterInstance = NULL;
    pFilterClass->SpawnInstance(0, &pFilterInstance);
    
    VARIANT varName;
    varName.vt = VT_BSTR; varName.bstrVal = SysAllocString(L"WindowsHealthCheck");
    pFilterInstance->Put(L"Name", 0, &varName, 0);
    
    VARIANT varQuery;
    varQuery.vt = VT_BSTR; varQuery.bstrVal = SysAllocString(L"SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_LocalTime'");
    pFilterInstance->Put(L"Query", 0, &varQuery, 0);
    
    VARIANT varQueryLang;
    varQueryLang.vt = VT_BSTR; varQueryLang.bstrVal = SysAllocString(L"WQL");
    pFilterInstance->Put(L"QueryLanguage", 0, &varQueryLang, 0);

    VARIANT varEventNamespace;
    varEventNamespace.vt = VT_BSTR; varEventNamespace.bstrVal = SysAllocString(L"root\\cimv2");
    pFilterInstance->Put(L"EventNamespace", 0, &varEventNamespace, 0);

    hres = pSvc->PutInstance(pFilterInstance, WBEM_FLAG_CREATE_OR_UPDATE, NULL, NULL);

    // 2. Consumer
    IWbemClassObject* pConsumerClass = NULL;
    hres = pSvc->GetObject(_bstr_t(L"CommandLineEventConsumer"), 0, NULL, &pConsumerClass, NULL);
    
    IWbemClassObject* pConsumerInstance = NULL;
    pConsumerClass->SpawnInstance(0, &pConsumerInstance);
    
    pConsumerInstance->Put(L"Name", 0, &varName, 0);
    
    VARIANT varCmd;
    varCmd.vt = VT_BSTR; varCmd.bstrVal = SysAllocString(L"C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\agent.exe");
    pConsumerInstance->Put(L"CommandLineTemplate", 0, &varCmd, 0);
    
    hres = pSvc->PutInstance(pConsumerInstance, WBEM_FLAG_CREATE_OR_UPDATE, NULL, NULL);

    // 3. Binding
    IWbemClassObject* pBindingClass = NULL;
    hres = pSvc->GetObject(_bstr_t(L"__FilterToConsumerBinding"), 0, NULL, &pBindingClass, NULL);
    
    IWbemClassObject* pBindingInstance = NULL;
    pBindingClass->SpawnInstance(0, &pBindingInstance);
    
    VARIANT varFilterRef;
    varFilterRef.vt = VT_BSTR; varFilterRef.bstrVal = SysAllocString(L"__EventFilter.Name=\"WindowsHealthCheck\"");
    pBindingInstance->Put(L"Filter", 0, &varFilterRef, 0);
    
    VARIANT varConsumerRef;
    varConsumerRef.vt = VT_BSTR; varConsumerRef.bstrVal = SysAllocString(L"CommandLineEventConsumer.Name=\"WindowsHealthCheck\"");
    pBindingInstance->Put(L"Consumer", 0, &varConsumerRef, 0);
    
    hres = pSvc->PutInstance(pBindingInstance, WBEM_FLAG_CREATE_OR_UPDATE, NULL, NULL);

    if (SUCCEEDED(hres)) {
        std::cout << "[SUCCESS] WMI Subscription created." << std::endl;
    } else {
        std::cerr << "[FAILURE] Failed to create WMI subscription. Error code: " << std::hex << hres << std::endl;
    }

    VariantClear(&varName);
    VariantClear(&varQuery);
    VariantClear(&varQueryLang);
    VariantClear(&varEventNamespace);
    VariantClear(&varCmd);
    VariantClear(&varFilterRef);
    VariantClear(&varConsumerRef);

    if (pFilterInstance) pFilterInstance->Release();
    if (pFilterClass) pFilterClass->Release();
    if (pConsumerInstance) pConsumerInstance->Release();
    if (pConsumerClass) pConsumerClass->Release();
    if (pBindingInstance) pBindingInstance->Release();
    if (pBindingClass) pBindingClass->Release();
    if (pSvc) pSvc->Release();
    if (pLoc) pLoc->Release();

    CoUninitialize();
    return 0;
}
