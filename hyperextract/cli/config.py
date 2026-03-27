"""Configuration management for Hyper-Extract CLI."""

import os
import json
import tomllib
import tomli_w
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


DEFAULT_CONFIG_DIR = Path.home() / ".he"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"


@dataclass
class LLMConfig:
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMConfig":
        return cls(
            model=data.get("model", "gpt-4o-mini"),
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", ""),
        )


@dataclass
class EmbedderConfig:
    model: str = "text-embedding-3-small"
    api_key: str = ""
    base_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbedderConfig":
        return cls(
            model=data.get("model", "text-embedding-3-small"),
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", ""),
        )


class ConfigManager:
    """Manages Hyper-Extract CLI configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or DEFAULT_CONFIG_FILE
        self.llm = LLMConfig()
        self.embedder = EmbedderConfig()
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            return

        with open(self.config_path, "rb") as f:
            data = tomllib.load(f)

        if "llm" in data:
            self.llm = LLMConfig.from_dict(data["llm"])
        if "embedder" in data:
            self.embedder = EmbedderConfig.from_dict(data["embedder"])

    def _save(self) -> None:
        """Save configuration to file."""
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "llm": self.llm.to_dict(),
            "embedder": self.embedder.to_dict(),
        }

        with open(self.config_path, "wb") as f:
            tomli_w.dump(data, f)

    def get_llm_config(self) -> LLMConfig:
        """Get LLM config with environment variable fallback."""
        config = LLMConfig(
            model=self.llm.model,
            api_key=self.llm.api_key or os.environ.get("OPENAI_API_KEY", ""),
            base_url=self.llm.base_url or os.environ.get("OPENAI_BASE_URL", ""),
        )
        return config

    def get_embedder_config(self) -> EmbedderConfig:
        """Get Embedder config with environment variable fallback."""
        config = EmbedderConfig(
            model=self.embedder.model,
            api_key=self.embedder.api_key or os.environ.get("OPENAI_API_KEY", ""),
            base_url=self.embedder.base_url or os.environ.get("OPENAI_BASE_URL", ""),
        )
        return config

    def set_llm(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        """Set LLM configuration."""
        if model:
            self.llm.model = model
        if api_key is not None:
            self.llm.api_key = api_key
        if base_url is not None:
            self.llm.base_url = base_url
        self._save()

    def set_embedder(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        """Set Embedder configuration."""
        if model:
            self.embedder.model = model
        if api_key is not None:
            self.embedder.api_key = api_key
        if base_url is not None:
            self.embedder.base_url = base_url
        self._save()

    def unset_llm(self) -> None:
        """Unset LLM configuration."""
        self.llm = LLMConfig()
        self._save()

    def unset_embedder(self) -> None:
        """Unset Embedder configuration."""
        self.embedder = EmbedderConfig()
        self._save()

    def show(self) -> Dict[str, Any]:
        """Show current configuration."""
        return {
            "llm": self.get_llm_config().to_dict(),
            "embedder": self.get_embedder_config().to_dict(),
        }

    def validate(self) -> tuple[bool, str]:
        """Validate configuration."""
        llm_config = self.get_llm_config()
        embedder_config = self.get_embedder_config()

        if not llm_config.api_key:
            return False, "LLM API key is not configured. Run 'he config llm --api-key YOUR_KEY'"

        if not embedder_config.api_key:
            return False, "Embedder API key is not configured. Run 'he config embedder --api-key YOUR_KEY'"

        return True, "Configuration is valid"


def load_kb_metadata(kb_path: Path) -> Optional[Dict[str, Any]]:
    """Load knowledge base metadata from directory."""
    metadata_path = kb_path / "metadata.json"
    if not metadata_path.exists():
        return None

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)
