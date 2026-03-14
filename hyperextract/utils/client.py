"""Client Factory - Create LLM and Embedder clients from config file."""

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

DEFAULT_CONFIG_DIR = Path.home() / ".he"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"


def get_client(config_path: Optional[Union[str, Path]] = None) -> Tuple:
    """Get LLM client and Embedder from config file.

    Args:
        config_path: Config file path, default ~/.he/config.toml

    Returns:
        (llm_client, embedder) tuple

    Examples:
        >>> from hyperextract.utils import get_client
        >>> llm, emb = get_client()
        >>> # Or with custom config path
        >>> llm, emb = get_client("/path/to/config.toml")
    """
    from hyperextract.cli.config import ConfigManager

    path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    manager = ConfigManager(path)

    llm_config = manager.get_llm_config()
    emb_config = manager.get_embedder_config()

    llm_client = _create_llm_client(llm_config)
    embedder = _create_embedder(emb_config)

    return llm_client, embedder


def _create_llm_client(config) -> "BaseChatModel":
    """Create LLM client from config."""
    if config.provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or os.environ.get("OPENAI_API_KEY", ""),
            base_url=config.base_url or None,
            temperature=0,
        )
    elif config.provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError(
                "Anthropic support requires the 'langchain-anthropic' package.\n"
                "Install it with one of:\n"
                "  pip install hyperextract[anthropic]\n"
                "  pip install langchain-anthropic"
            )

        return ChatAnthropic(
            model=config.model,
            api_key=config.api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        )
    elif config.provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "Google support requires the 'langchain-google-genai' package.\n"
                "Install it with one of:\n"
                "  pip install hyperextract[google]\n"
                "  pip install langchain-google-genai"
            )

        return ChatGoogleGenerativeAI(
            model=config.model,
            google_api_key=config.api_key or os.environ.get("GOOGLE_API_KEY", ""),
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")


def _create_embedder(config) -> "Embeddings":
    """Create Embedder from config."""
    if config.provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=config.model,
            api_key=config.api_key or os.environ.get("OPENAI_API_KEY", ""),
            base_url=config.base_url or None,
        )
    elif config.provider == "anthropic":
        try:
            from langchain_anthropic import AnthropicEmbeddings
        except ImportError:
            raise ImportError(
                "Anthropic support requires the 'langchain-anthropic' package.\n"
                "Install it with one of:\n"
                "  pip install hyperextract[anthropic]\n"
                "  pip install langchain-anthropic"
            )

        return AnthropicEmbeddings(
            model=config.model,
            api_key=config.api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        )
    elif config.provider == "google":
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError:
            raise ImportError(
                "Google support requires the 'langchain-google-genai' package.\n"
                "Install it with one of:\n"
                "  pip install hyperextract[google]\n"
                "  pip install langchain-google-genai"
            )

        return GoogleGenerativeAIEmbeddings(
            model=config.model,
            google_api_key=config.api_key or os.environ.get("GOOGLE_API_KEY", ""),
        )
    else:
        raise ValueError(f"Unsupported Embedder provider: {config.provider}")
