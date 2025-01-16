import logging
import shutil
from pathlib import Path
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS


logger = logging.getLogger(__name__)


class FaissVectorDB:
    """
    Manages multiple FAISS indexes for different embedding sources.
    """

    def __init__(self, dimension: int, embeddings):
        """
        Initializes multiple FAISS indexes.
        """

        index = faiss.IndexFlatL2(dimension)
        self.vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        self.vector_store_path = Path(__file__).resolve().parent / "vector_store"

    async def search(self, query: str, top_k: int, source: str):
        """
        Search for the top-k similar embeddings in the specified FAISS index.
        """
        retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold", search_kwargs={"k": top_k}
        )
        res = await retriever.ainvoke(query, filter={"source": source})

        return res

    async def add_documents_in_batches(self, documents, ids, batch_size=200):
        """
        Add documents to the vector store in batches.
        
        :param vector_store: The vector store object.
        :param documents: List of documents to add.
        :param ids: List of document IDs corresponding to the documents.
        :param batch_size: The size of each batch.
        """
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            try:
                await self.vector_store.aadd_documents(documents=batch_docs, ids=batch_ids)
            except Exception as e:
                print(f"Error during aadd_documents: {e}")
            
    def save_indexes(self):
        self.vector_store.save_local(self.vector_store_path)

    def clear_indexes(self):
        folder = self.vector_store_path
        if folder.exists() and folder.is_dir():
            shutil.rmtree(folder)
            print(f"Removed Faiss indexes: {folder}")
        else:
            print(f"Faiss Indexes folder does not exist: {folder}")
