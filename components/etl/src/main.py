import asyncio
from pathlib import Path

from extractor import CSVDataExtractor
from mongodb_loader import MongoDBLoader
from vector_store import FaissVectorDB
from transformer import DataTransformer
from config import Config
from langchain_huggingface import HuggingFaceEmbeddings


class ETLProcess:
    """
    Orchestrates the ETL pipeline: extract from CSV, transform, load into MongoDB and FAISS.
    """

    def __init__(
        self,
        extractor: CSVDataExtractor,
        transformer: DataTransformer,
        mongodb_loader: MongoDBLoader,
        faiss_vectordb: FaissVectorDB,
    ):
        self.extractor = extractor
        self.transformer = transformer
        self.mongodb_loader = mongodb_loader
        self.faiss_vectordb = faiss_vectordb

    async def run(self, clear_existing: bool = True):
        """
        Executes the ETL pipeline: extraction, transformation, and loading.

        Args:
            clear_existing (bool): Whether to clear existing data in MongoDB and FAISS.
        """
        # Optionally clear existing data in MongoDB and FAISS
        if clear_existing:
            print("Clearing existing data...")
            await self.mongodb_loader.clear_collections()
            self.faiss_vectordb.clear_indexes()

        print("Starting ETL process...")
        for i, chunk_df in enumerate(self.extractor.extract_data(), start=1):
            print(f"Processing batch {i}...")
            transformed_df = self.transformer.transform_chunk(chunk_df)
            await self.mongodb_loader.insert_documents(transformed_df)
        print("ETL process complete!")

        await self.mongodb_loader.close_connection()


async def main():
    config = Config()
    data_file = Path("data") / "PURCHASE ORDER DATA EXTRACT 2012-2015_0.csv"

    extractor = CSVDataExtractor(csv_file=data_file, chunk_size=10000)
    print("Loading HuggingFace Embedding model...")
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
        cache_folder="embeddings_cache",
    )
    print("Loaded HuggingFace Embedding model...")

    transformer = DataTransformer()
    faiss_vectordb = FaissVectorDB(
        dimension=768,
        embeddings=embeddings,
    )
    mongodb_loader = MongoDBLoader(
        host=config.mongodb.HOST,
        port=config.mongodb.PORT,
        username=config.mongodb.USERNAME,
        password=config.mongodb.PASSWORD,
        db_name=config.mongodb.DB_NAME,
        orders_collection="Orders",
        vectordb=faiss_vectordb,
    )

    etl = ETLProcess(extractor, transformer, mongodb_loader, faiss_vectordb)
    await etl.run(clear_existing=True)


if __name__ == "__main__":
    asyncio.run(main())
