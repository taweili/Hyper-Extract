"""Client Factory - Create OpenAI LLM and Embedder clients from config."""

import os
from pathlib import Path
from typing import Tuple

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

DEFAULT_CONFIG_DIR = Path.home() / ".he"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"


def get_client(config_path: str|Path = None) -> Tuple[BaseChatModel, Embeddings]:
    """Get OpenAI LLM client and Embedder from config.

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

    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    llm_client = ChatOpenAI(
        model=llm_config.model,
        api_key=llm_config.api_key or os.environ.get("OPENAI_API_KEY", ""),
        base_url=llm_config.base_url or None,
        temperature=0,
    )

    embedder = OpenAIEmbeddings(
        model=emb_config.model,
        api_key=emb_config.api_key or os.environ.get("OPENAI_API_KEY", ""),
        base_url=emb_config.base_url or None,
    )

    return llm_client, embedder
