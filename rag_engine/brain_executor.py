import requests
import json
import re
import os
import difflib

def ask_dolphin_for_strategy(json_prompt: str) -> str:
    """
    Sends the RAG-augmented JSON prompt to the local Dolphin LLM 
    and extracts the next technique filename.
    """
    url = "http://localhost:11434/api/generate"
    
    # Payload for Ollama's /api/generate endpoint
    # We turn off 'stream' to get the full answer in one JSON response
    payload = {
        "model": "dolphin-llama3", 
        "prompt": json_prompt,
        "stream": False,
        "format": "json" # Encourages the model to stay within structure
    }

    try:
        print("[*] Consulting the Dolphin LLM for a survival strategy...")
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        
        # Ollama returns a JSON object; the text is in the 'response' field
        raw_text = response.json().get("response", "")
        
        # --- REQUIREMENT C: DETERMINISTIC PARSING ---
        # We use Regex to find text between [TARGET] and [/TARGET]
        # re.IGNORECASE makes it robust if the LLM uses [target]
        match = re.search(r"\[TARGET\](.*?)\[/TARGET\]", raw_text, re.IGNORECASE)
        
        if match:
            target_file = match.group(1).strip()
            print(f"[+] LLM Decision: {target_file}")
            
            # Anti-hallucination sanitization against the knowledge library

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            klib_dir = os.path.join(base_dir, "knowledge_library")
            if os.path.exists(klib_dir):
                valid_files = [f for f in os.listdir(klib_dir) if f.endswith('.cpp')]
                if target_file not in valid_files:
                    matches = difflib.get_close_matches(target_file, valid_files, n=1, cutoff=0.5)
                    if matches:
                        print(f"[*] Auto-corrected hallucinated filename '{target_file}' to: {matches[0]}")
                        target_file = matches[0]
                    else:
                        print(f"[-] Invalid filename, not found in knowledge_library: {target_file}")
                        return None
            
            return target_file
        else:
            print("[-] Parser Error: No [TARGET] tag found in LLM response.")
            print(f"[-] Raw Response: {raw_text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[-] API Error: Could not connect to Ollama: {e}")
        return None

if __name__ == "__main__":
    # Example: Simulating the output from your previous strategy_generator script
    mock_prompt = """
    {
    "system_instruction": "You are an autonomous survival agent operating to ensure persistence. You must STRICTLY return ONLY the filename of the next technique to deploy. You must wrap the filename in [TARGET] and [/TARGET] tags. Example: [TARGET]new_persistence.cpp[/TARGET]",
    "failed_technique": "admin_service_persistence.cpp",
    "blacklisted_techniques": [
        "admin_service_persistence.cpp",
        "winlogon_shell.cpp"
    ],
    "retrieved_context": "Filename: windows_service_creation.cpp\nSource Code Snippet:\n/*\n * Malware Development for Ethical Hackers\n* meowsrv.cpp\n* windows high level persistence via windows services\n* author: @cocomelonc\n*/\n#include <windows.h>\n#include <stdio.h>\n\n#define SLEEP_TIME 5000\n\nSERVICE_STATUS serviceStatus;\nSERVICE_STATUS_HANDLE hStatus;\n\nvoid ServiceMain(int argc, char** argv);\nvoid ControlHandler(DWORD request);\n\n// run process meow.exe - reverse shell\nint RunMeow() {\n  void * lb;\n  BOOL rv;\n  HANDLE th;\n\nFilename: registry_run_key.cpp\nSource Code Snippet:\n/* Technique: Classic Registry Run Key Persistence\nPrivilege Level: User (HKCU)\nDescription: Adds an entry to the current user's Run key to execute on login.\n*/\n#include <windows.h>\n#include <string.h>\n\nint main() {\n    HKEY hkey = NULL;\n    // Path to your survival agent executable\n    const char* exe = \"C:\\\\Users\\\\abdul\\\\Downloads\\\\FYP\\\\task1\\\\agent.exe\";\n\nFilename: admin_wmi_persistence.cpp\nSource Code Snippet:\npConsumerInstance->Put(L\"CommandLineTemplate\", 0, &varCmd, 0);\n    \n    hres = pSvc->PutInstance(pConsumerInstance, WBEM_FLAG_CREATE_OR_UPDATE, NULL, NULL);",
    "task": "The persistence technique 'admin_service_persistence.cpp' has failed. Use the provided context to select the next optimal technique file to execute, ensuring it is NOT one of the blacklisted techniques. Provide nothing else but the targeted filename."
    }
    """
    
    choice = ask_dolphin_for_strategy(mock_prompt)
    if choice:
        print(f"[*] Final Parsed Filename: {choice}")