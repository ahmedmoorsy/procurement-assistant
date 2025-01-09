import logging
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class MongoDBService:
    """
    Loads transformed data into a single MongoDB collection and performs queries or aggregation.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        db_name: str,
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
        self.orders_collection = self.db[orders_collection]

    async def aggregate_orders(
        self, pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Runs an aggregation query on the orders collection.

        Args:
            pipeline (List[Dict[str, Any]]): MongoDB aggregation pipeline.

        Returns:
            List[Dict[str, Any]]: Aggregated results.
        """
        cursor = self.orders_collection.aggregate(pipeline)
        return [doc async for doc in cursor]

    async def close_connection(self) -> None:
        """
        Closes the MongoDB connection.
        """
        logger.info("Closing MongoDB connection.")
        self.client.close()
