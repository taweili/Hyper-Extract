"""Extraction models and prompt builder."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel


class GuidelineTarget(BaseModel):
    """Extraction target with role definition and content description."""

    zh: Optional[str] = None
    en: Optional[str] = None

    @classmethod
    def from_value(cls, value: Union[str, Dict[str, str], None]) -> Optional["GuidelineTarget"]:
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


class Guideline(BaseModel):
    """Extraction guideline configuration."""

    target: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules_for_entities: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
    rules_for_relations: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None
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
        "entity_extraction_rules": "实体提取规则",
        "relation_extraction_rules": "关系提取规则",
        "time_rules": "时间规则",
        "location_rules": "位置规则",
        "role_and_task": "角色与任务",
    },
    "en": {
        "source_text": "Source Text",
        "known_entities": "Known Entities",
        "extraction_rules": "Extraction Rules",
        "entity_extraction_rules": "Entity Extraction Rules",
        "relation_extraction_rules": "Relation Extraction Rules",
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

    def build_target(self, guideline: Guideline) -> Optional[str]:
        """Build target field (role definition + extraction content description)."""
        target = guideline.target
        if target is None:
            return None
        return self._get_text(target, self.language)

    def build_rules(self, guideline: Guideline) -> Optional[str]:
        """Build rules field (with title)."""
        rules = self._get_text(guideline.rules, self.language)
        if rules:
            return self._add_title(rules, "extraction_rules")
        return None

    def build_rules_for_entities(self, guideline: Guideline) -> Optional[str]:
        """Build rules_for_entities field (with title)."""
        rules = self._get_text(guideline.rules_for_entities, self.language)
        if rules:
            return self._add_title(rules, "entity_extraction_rules")
        return None

    def build_rules_for_relations(self, guideline: Guideline) -> Optional[str]:
        """Build rules_for_relations field (with title)."""
        rules = self._get_text(guideline.rules_for_relations, self.language)
        if rules:
            return self._add_title(rules, "relation_extraction_rules")
        return None

    def build_rules_for_time(self, guideline: Guideline) -> Optional[str]:
        """Build rules_for_time field (with title)."""
        rules = self._get_text(guideline.rules_for_time, self.language)
        if rules:
            return self._add_title(rules, "time_rules")
        return None

    def build_rules_for_location(self, guideline: Guideline) -> Optional[str]:
        """Build rules_for_location field (with title)."""
        rules = self._get_text(guideline.rules_for_location, self.language)
        if rules:
            return self._add_title(rules, "location_rules")
        return None

    def build_model_prompt(self, guideline: Guideline) -> str:
        """Build Model/List/Set type Prompt."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules = self.build_rules(guideline)
        if rules:
            parts.append(rules)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_main_prompt(self, guideline: Guideline) -> str:
        """Build Graph type main Prompt (single-stage mode)."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules_for_entities = self.build_rules_for_entities(guideline)
        if rules_for_entities:
            parts.append(rules_for_entities)

        rules_for_relations = self.build_rules_for_relations(guideline)
        if rules_for_relations:
            parts.append(rules_for_relations)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_entity_prompt(self, guideline: Guideline) -> str:
        """Build Graph type entity extraction Prompt (two-stage mode)."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules_for_entities = self.build_rules_for_entities(guideline)
        if rules_for_entities:
            parts.append(rules_for_entities)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_relation_prompt(self, guideline: Guideline) -> str:
        """Build Graph type relation extraction Prompt (two-stage mode)."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules_for_relations = self.build_rules_for_relations(guideline)
        if rules_for_relations:
            parts.append(rules_for_relations)

        known_label = self.labels.get("known_entities", "已知实体")
        parts.append(f"## {known_label}:\n{{known_nodes}}")

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_temporal_graph_entity_prompt(self, guideline: Guideline) -> str:
        """Build TemporalGraph entity extraction Prompt."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules_for_entities = self.build_rules_for_entities(guideline)
        if rules_for_entities:
            parts.append(rules_for_entities)

        rules_for_time = self.build_rules_for_time(guideline)
        if rules_for_time:
            parts.append(rules_for_time)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_spatial_graph_entity_prompt(self, guideline: Guideline) -> str:
        """Build SpatialGraph entity extraction Prompt."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules_for_entities = self.build_rules_for_entities(guideline)
        if rules_for_entities:
            parts.append(rules_for_entities)

        rules_for_location = self.build_rules_for_location(guideline)
        if rules_for_location:
            parts.append(rules_for_location)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_spatio_temporal_graph_entity_prompt(self, guideline: Guideline) -> str:
        """Build SpatioTemporalGraph entity extraction Prompt."""
        parts = []

        target = self.build_target(guideline)
        if target:
            parts.append(target)

        rules_for_entities = self.build_rules_for_entities(guideline)
        if rules_for_entities:
            parts.append(rules_for_entities)

        rules_for_time = self.build_rules_for_time(guideline)
        if rules_for_time:
            parts.append(rules_for_time)

        rules_for_location = self.build_rules_for_location(guideline)
        if rules_for_location:
            parts.append(rules_for_location)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)


__all__ = [
    "GuidelineTarget",
    "Guideline",
    "PromptBuilder",
]
