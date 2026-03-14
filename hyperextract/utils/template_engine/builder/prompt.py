"""Extraction models and prompt builder."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel


class GuideTarget(BaseModel):
    """Extraction target with role definition and content description."""

    zh: Optional[str] = None
    en: Optional[str] = None

    @classmethod
    def from_value(cls, value: Union[str, Dict[str, str], None]) -> Optional["GuideTarget"]:
        """Create instance from string or dict."""
        if value is None:
            return None
        if isinstance(value, str):
            return cls(zh=value)
        if isinstance(value, dict):
            return cls(**value)
        return None

    def get(self, language: str = "zh") -> str:
        """Get content for specified language."""
        return getattr(self, language) or self.zh or ""


class Guide(BaseModel):
    """Guide configuration."""

    target: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules_for_nodes: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules_for_edges: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules_for_time: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules_for_location: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None

    def get_field(self, field_name: str, language: str = "zh") -> Optional[str]:
        """Get specified field content for specified language."""
        value = getattr(self, field_name, None)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(value))
        if isinstance(value, dict):
            dict_value = value.get(language) or value.get("zh")
            if dict_value is None:
                return None
            if isinstance(dict_value, str):
                return dict_value
            if isinstance(dict_value, list):
                return "\n".join(f"{i+1}. {item}" for i, item in enumerate(dict_value))
        return None


LABEL_MAPPING = {
    "zh": {
        "source_text": "源文本",
        "known_entities": "已知实体",
        "extraction_rules": "提取规则",
        "node_extraction_rules": "节点提取规则",
        "edge_extraction_rules": "边提取规则",
        "time_rules": "时间规则",
        "location_rules": "位置规则",
        "role_and_task": "角色与任务",
    },
    "en": {
        "source_text": "Source Text",
        "known_entities": "Known Entities",
        "extraction_rules": "Extraction Rules",
        "node_extraction_rules": "Node Extraction Rules",
        "edge_extraction_rules": "Edge Extraction Rules",
        "time_rules": "Time Rules",
        "location_rules": "Location Rules",
        "role_and_task": "Role and Task",
    },
}


class PromptBuilder:
    """Prompt Builder - Builds extraction prompts for various AutoType."""

    def __init__(self, language: str = "zh"):
        """Initialize Prompt Builder."""
        self.language = language
        self.labels = LABEL_MAPPING.get(language, LABEL_MAPPING["zh"])

    @staticmethod
    def _get_text(value: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]], language: str = "zh") -> Optional[str]:
        """Get multilingual text value, supports list format."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(value))
        if isinstance(value, dict):
            dict_value = value.get(language) or value.get("zh")
            if dict_value is None:
                return None
            if isinstance(dict_value, str):
                return dict_value
            if isinstance(dict_value, list):
                return "\n".join(f"{i+1}. {item}" for i, item in enumerate(dict_value))
        return None

    def _add_title(self, text: str, title_key: str) -> str:
        """Add title to text."""
        title = self.labels.get(title_key, title_key)
        return f"### {title}\n{text}"

    def build_target(self, guide: Guide) -> Optional[str]:
        """Build target field (role definition + extraction content description)."""
        target = guide.target
        if target is None:
            return None
        return self._get_text(target, self.language)

    def build_rules(self, guide: Guide) -> Optional[str]:
        """Build rules field (with title)."""
        rules = self._get_text(guide.rules, self.language)
        if rules:
            return self._add_title(rules, "extraction_rules")
        return None

    def build_rules_for_nodes(self, guide: Guide) -> Optional[str]:
        """Build rules_for_nodes field (with title)."""
        rules = self._get_text(guide.rules_for_nodes, self.language)
        if rules:
            return self._add_title(rules, "node_extraction_rules")
        return None

    def build_rules_for_edges(self, guide: Guide) -> Optional[str]:
        """Build rules_for_edges field (with title)."""
        rules = self._get_text(guide.rules_for_edges, self.language)
        if rules:
            return self._add_title(rules, "edge_extraction_rules")
        return None

    def build_rules_for_time(self, guide: Guide) -> Optional[str]:
        """Build rules_for_time field (with title)."""
        rules = self._get_text(guide.rules_for_time, self.language)
        if rules:
            return self._add_title(rules, "time_rules")
        return None

    def build_rules_for_location(self, guide: Guide) -> Optional[str]:
        """Build rules_for_location field (with title)."""
        rules = self._get_text(guide.rules_for_location, self.language)
        if rules:
            return self._add_title(rules, "location_rules")
        return None

    def build_model_prompt(self, guide: Guide) -> str:
        """Build Model/List/Set type Prompt."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules = self.build_rules(guide)
        if rules:
            parts.append(rules)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_main_prompt(self, guide: Guide) -> str:
        """Build Graph type main Prompt (single-stage mode)."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_edges = self.build_rules_for_edges(guide)
        if rules_for_edges:
            parts.append(rules_for_edges)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_node_prompt(self, guide: Guide) -> str:
        """Build Graph type node extraction Prompt (two-stage mode)."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_edge_prompt(self, guide: Guide) -> str:
        """Build Graph type edge extraction Prompt (two-stage mode)."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules_for_edges = self.build_rules_for_edges(guide)
        if rules_for_edges:
            parts.append(rules_for_edges)

        known_label = self.labels.get("known_entities", "已知实体")
        parts.append(f"## {known_label}:\n{{known_nodes}}")

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_temporal_graph_node_prompt(self, guide: Guide) -> str:
        """Build TemporalGraph node extraction Prompt."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_time = self.build_rules_for_time(guide)
        if rules_for_time:
            parts.append(rules_for_time)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_spatial_graph_node_prompt(self, guide: Guide) -> str:
        """Build SpatialGraph node extraction Prompt."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_location = self.build_rules_for_location(guide)
        if rules_for_location:
            parts.append(rules_for_location)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_spatio_temporal_graph_node_prompt(self, guide: Guide) -> str:
        """Build SpatioTemporalGraph node extraction Prompt."""
        parts = []

        target = self.build_target(guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_time = self.build_rules_for_time(guide)
        if rules_for_time:
            parts.append(rules_for_time)

        rules_for_location = self.build_rules_for_location(guide)
        if rules_for_location:
            parts.append(rules_for_location)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)


__all__ = [
    "GuideTarget",
    "Guide",
    "PromptBuilder",
]
