from langchain.chat_models import init_chat_model
from config import Config


def initialize_llm(config: Config):
    """
    Initializes the LLM based on the project configuration.

    :param config: The Config object containing all settings.
    :return: An initialized LLM instance.
    """
    # Map model providers to their respective configurations
    provider_config_map = {
        "azure_openai": {
            "model": config.azure_llm.MODEL,
            "model_provider": config.azure_llm.MODEL_PROVIDER,
            "temperature": config.azure_llm.TEMPERATURE,
            "api_key": config.azure_llm.API_KEY,
            "openai_api_version": config.azure_llm.OPENAI_API_VERSION,
            "azure_endpoint": config.azure_llm.AZURE_ENDPOINT,
            "azure_deployment": config.azure_llm.DEPLOYMENT_NAME,
        },
        "openai": {
            "model": config.openai_llm.MODEL,
            "model_provider": config.openai_llm.MODEL_PROVIDER,
            "temperature": config.openai_llm.TEMPERATURE,
            "api_key": config.openai_llm.API_KEY,
        },
    }

    model_provider = config.project.model_provider
    if model_provider not in provider_config_map:
        raise ValueError(f"Unsupported model provider: {model_provider}")

    user_config = provider_config_map[model_provider]

    return init_chat_model(**user_config)


config = Config()
llm = initialize_llm(config)
