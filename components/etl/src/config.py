from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class MongoDB(BaseSettings):
    """
    MongoDB Configuration using Pydantic BaseSettings
    """

    HOST: str = Field(default="localhost", alias="MONGO_HOST")
    PORT: int = Field(default=27017, alias="MONGO_PORT")
    USERNAME: str = Field(default="root", alias="MONGO_USERNAME")
    PASSWORD: str = Field(default="password", alias="MONGO_PASSWORD")
    DB_NAME: str = Field(default="procurementDB", alias="MONGO_DB_NAME")


class Embedding(BaseSettings):
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        alias="EMBEDDING_EMBEDDING_MODEL",
    )


class Config(BaseSettings):
    mongodb: MongoDB = Field(default_factory=MongoDB)
    embedding: Embedding = Field(default_factory=Embedding)
