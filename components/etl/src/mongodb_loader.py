import asyncio
import logging
import pandas as pd
from urllib.parse import quote_plus
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_core.documents import Document
from uuid import uuid4


logger = logging.getLogger(__name__)


class MongoDBLoader:
    """
    Loads transformed data into a single MongoDB collection and optionally retrieves
    embeddings for FAISS indexing.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        db_name: str,
        vectordb,
        orders_collection: str = "orders",
    ):
        """
        Initializes the MongoDB connection with authentication.

        Args:
            host (str): MongoDB host address.
            port (int): MongoDB port number.
            username (str): Username for MongoDB authentication.
            password (str): Password for MongoDB authentication.
            db_name (str): Name of the database.
            orders_collection (str): Collection name for combined orders and line items.
        """
        username_quoted = quote_plus(username)
        password_quoted = quote_plus(password)
        mongo_uri = f"mongodb://{username_quoted}:{password_quoted}@{host}:{port}/"

        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.orders_collection = orders_collection
        self.vectordb = vectordb

        logger.info("MongoDBLoader initialized.")

    async def clear_collections(self) -> None:
        """
        Clear existing data from the collection.
        """
        logger.info("Clearing the collection...")
        await self.db[self.orders_collection].delete_many({})
        logger.info("Collection cleared successfully.")

    async def insert_documents(self, df: pd.DataFrame, chunk_size: int = 10000):
        """
        Insert documents into two collections: purchaseOrders & lineItems.
        Includes validation for required columns and data types.

        Args:
            df (pd.DataFrame): The DataFrame containing the records to insert.
            chunk_size (int): Number of rows to insert in a single batch.

        Returns:
            List[Tuple]: A list of tuples (mongo_id, embedding) for FAISS indexing.
        """

        required_cols_po = {
            "Purchase Order Number": str,
            "Creation Date": str,
            "Purchase Date": str,
            "Fiscal Year": str,
            "Department Name": str,
            "Supplier Name": str,
            "Supplier Code": str,
            "Supplier Qualifications": str,
            "Acquisition Type": str,
            "Acquisition Method": str,
            "CalCard": str,
        }

        required_cols_li = {
            "Purchase Order Number": str,
            "Item Name": str,
            "Item Description": str,
            "Quantity": float,
            "Unit Price": float,
            "Total Price": float,
            "Normalized UNSPSC": str,
            "Commodity Title": str,
        }

        all_required_cols = {**required_cols_po, **required_cols_li}
        missing_cols = [col for col in all_required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        for col, col_type in all_required_cols.items():
            if col in ["Creation Date", "Purchase Date"]:
                try:
                    df[col] = pd.to_datetime(df[col], errors="raise")
                except Exception as e:
                    raise ValueError(
                        f"Column '{col}' cannot be converted to datetime: {e}"
                    )
            else:
                try:
                    df[col] = df[col].astype(col_type)
                except ValueError as e:
                    raise ValueError(
                        f"Column '{col}' cannot be converted to {col_type}: {e}"
                    )

        num_rows = len(df)
        logger.info(f"Starting insert for {num_rows} rows in chunks of {chunk_size}.")

        for start_idx in range(0, num_rows, chunk_size):
            end_idx = min(start_idx + chunk_size, num_rows)
            df_chunk = df.iloc[start_idx:end_idx]

            orders = []
            docs = []
            docs_ids = []

            for idx, row in df_chunk.iterrows():
                try:
                    commodity_title_uuid = str(uuid4())
                    item_desc_uuid = str(uuid4())
                    docs_ids.extend([commodity_title_uuid, item_desc_uuid])

                    order_doc = {
                        "purchaseOrderNumber": row["Purchase Order Number"],
                        "creationDate": row["Creation Date"],
                        "purchaseDate": row["Purchase Date"],
                        "fiscalYear": row["Fiscal Year"],
                        "departmentName": row["Department Name"],
                        "supplierName": row["Supplier Name"],
                        "supplierCode": row["Supplier Code"],
                        "supplierQualifications": row["Supplier Qualifications"],
                        "acquisitionType": row["Acquisition Type"],
                        "acquisitionMethod": row["Acquisition Method"],
                        "calCardUsed": row["CalCard"],
                        "lineItems": [
                            {
                                "itemName": row["Item Name"],
                                "itemDescription": row["Item Description"],
                                "itemDescriptionUUID": item_desc_uuid,
                                "quantity": row["Quantity"],
                                "unitPrice": row["Unit Price"],
                                "totalPrice": row["Total Price"],
                                "normalizedUNSPSC": row["Normalized UNSPSC"],
                                "commodityTitle": row["Commodity Title"],
                                "commodityTitleUUID": commodity_title_uuid,
                            }
                        ],
                    }
                    orders.append(order_doc)

                    docs.append(
                        Document(
                            page_content=row["Item Description"],
                            metadata={"source": "Item Description"},
                        )
                    )
                    docs.append(
                        Document(
                            page_content=row["Commodity Title"],
                            metadata={"source": "Commodity Title"},
                        )
                    )
                except KeyError as e:
                    raise ValueError(f"Missing required field in row: {e}")
                except Exception as e:
                    raise ValueError(f"Error processing row: {e}")

            await self._bulk_insert(orders, docs, docs_ids)
            logger.info(f"Inserted rows {start_idx} to {end_idx - 1}.")

        self.vectordb.save_indexes()

    async def _bulk_insert(self, orders: list, docs: list, docs_ids: list):
        """
        Performs the actual bulk insert into MongoDB and collects FAISS data.

        Args:
            orders (list): List of combined order documents.
            docs (list): List of documents for FAISS indexing.
            docs_ids (list): List of document IDs for FAISS indexing.
        """
        try:
            await self.db[self.orders_collection].insert_many(orders)
            # await self.vectordb.vector_store.aadd_documents(documents=docs, ids=docs_ids)
        except Exception as e:
            logger.error(f"Failed to insert documents into MongoDB or vector DB: {e}")
            raise RuntimeError(
                f"Failed to insert documents into MongoDB or vector DB: {e}"
            )

    async def close_connection(self) -> None:
        """
        Closes the MongoDB connection.
        """
        logger.info("Closing MongoDB connection.")
        self.client.close()
