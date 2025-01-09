from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


load_dotenv()


class Project(BaseSettings):
    model_provider: str = "azure_openai"


class MongoDB(BaseSettings):
    """
    MongoDB Configuration using Pydantic BaseSettings
    """

    HOST: str = Field(default="localhost", alias="MONGO_HOST")
    PORT: int = Field(default=27017, alias="MONGO_PORT")
    USERNAME: str = Field(default="root", alias="MONGO_USERNAME")
    PASSWORD: str = Field(default="password", alias="MONGO_PASSWORD")
    DB_NAME: str = Field(default="procurementDB", alias="MONGO_DB_NAME")


class AzureLLMConfig(BaseSettings):
    MODEL: str = "gpt-4o"
    MODEL_PROVIDER: str = "azure_openai"
    TEMPERATURE: int = 0
    DEPLOYMENT_NAME: str = "gpt-4o"
    API_KEY: str = Field(default="", alias="AZURE_API_KEY")
    OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_ENDPOINT: str = "https://example-ai.openai.azure.com"


class OpenAILLMConfig(BaseSettings):
    MODEL: str = "gpt-4o"
    MODEL_PROVIDER: str = "openai"
    TEMPERATURE: int = 0
    API_KEY: str = Field(default="", alias="OPENAI_API_KEY")


class Config(BaseSettings):
    project: Project = Field(default_factory=Project)
    mongodb: MongoDB = Field(default_factory=MongoDB)
    openai_llm: OpenAILLMConfig = Field(default_factory=OpenAILLMConfig)
    azure_llm: AzureLLMConfig = Field(default_factory=AzureLLMConfig)
