import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS

class LibraryIndexer:
    def __init__(self, source_dir: str = None, vector_store_dir: str = None):
        """
        Initialize the LibraryIndexer.
        :param source_dir: Directory containing the code/files to be indexed.
        :param vector_store_dir: Directory where the FAISS vector index will be saved.
        """
        # Define paths relative to the project root (parent directory of this script's folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_dir = source_dir if source_dir else os.path.join(base_dir, "knowledge_library")
        self.vector_store_dir = vector_store_dir if vector_store_dir else os.path.join(base_dir, "vector_store")

    def run(self):
        """
        Reads files from the source directory, splits them into chunks,
        generates embeddings, and saves the vector store locally.
        """
        try:
            print(f"[*] Loading documents from '{self.source_dir}'...")
            
            # Using TextLoader for parsing plain text / cpp files to minimize dependencies.
            # We specifically target .cpp files to avoid reading binary files like .exe
            loader = DirectoryLoader(self.source_dir, glob="**/*.cpp", loader_cls=TextLoader)
            all_documents = loader.load()

            ignore_file = "windows_service_creation.cpp"
            documents = [
                doc for doc in all_documents 
                if os.path.basename(doc.metadata['source']) != ignore_file
            ]
            print(f"[+] Successfully loaded {len(documents)} document(s) (ignored {ignore_file}).")

            print("[*] Splitting text into 500-character segments...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50  # Adding a 50-character overlap helps preserve context between chunks
            )
            docs = text_splitter.split_documents(documents)
            print(f"[+] Split documents into {len(docs)} chunk(s).")

            print("[*] Generating embeddings using local FastEmbed ONNX model...")
            # FastEmbed natively uses ONNX Runtime which completely bypasses the PyTorch Win DLL initialization bug.
            # It runs fully locally and is specifically built for maximum speed.
            embeddings = FastEmbedEmbeddings()

            print("[*] Building FAISS vector store...")
            vector_store = FAISS.from_documents(docs, embeddings)

            print(f"[*] Saving index locally to '{self.vector_store_dir}'...")
            os.makedirs(self.vector_store_dir, exist_ok=True)
            vector_store.save_local(self.vector_store_dir)
            print("[+] Done! Vector store saved successfully.")

        except Exception as e:
            print(f"[-] An error occurred during indexing: {e}")

if __name__ == "__main__":
    # Ensures the code runs on execution for easy debugging.
    indexer = LibraryIndexer()
    indexer.run()
