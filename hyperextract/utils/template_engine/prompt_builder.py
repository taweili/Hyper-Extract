"""Prompt Builder - Builds extraction prompts for various AutoType.

Supports extraction_guide target field, automatically adds titles to rules.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .config_loader import ExtractionGuide


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
    """Prompt Builder."""

    def __init__(self, language: str = "zh"):
        """Initialize Prompt Builder."""
        self.language = language
        self.labels = LABEL_MAPPING.get(language, LABEL_MAPPING["zh"])

    @staticmethod
    def _get_text(value: Optional[Union[List[str], Dict[str, List[str]]]], language: str = "zh") -> Optional[str]:
        """Get multilingual text value, supports list format."""
        if value is None:
            return None
        if isinstance(value, list):
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(value))
        if isinstance(value, dict):
            dict_value = value.get(language) or value.get("zh")
            if dict_value is None:
                return None
            if isinstance(dict_value, list):
                return "\n".join(f"{i+1}. {item}" for i, item in enumerate(dict_value))
        return None

    def _add_title(self, text: str, title_key: str) -> str:
        """Add title to text."""
        title = self.labels.get(title_key, title_key)
        return f"### {title}\n{text}"

    def build_target(self, extraction_guide: ExtractionGuide) -> Optional[str]:
        """Build target field (role definition + extraction content description)."""
        target = extraction_guide.target
        if target is None:
            return None
        return self._get_text(target, self.language)

    def build_rules(self, extraction_guide: ExtractionGuide) -> Optional[str]:
        """Build rules field (with title)."""
        rules = self._get_text(extraction_guide.rules, self.language)
        if rules:
            return self._add_title(rules, "extraction_rules")
        return None

    def build_rules_for_nodes(self, extraction_guide: ExtractionGuide) -> Optional[str]:
        """Build rules_for_nodes field (with title)."""
        rules = self._get_text(extraction_guide.rules_for_nodes, self.language)
        if rules:
            return self._add_title(rules, "node_extraction_rules")
        return None

    def build_rules_for_edges(self, extraction_guide: ExtractionGuide) -> Optional[str]:
        """Build rules_for_edges field (with title)."""
        rules = self._get_text(extraction_guide.rules_for_edges, self.language)
        if rules:
            return self._add_title(rules, "edge_extraction_rules")
        return None

    def build_rules_for_time(self, extraction_guide: ExtractionGuide) -> Optional[str]:
        """Build rules_for_time field (with title)."""
        rules = self._get_text(extraction_guide.rules_for_time, self.language)
        if rules:
            return self._add_title(rules, "time_rules")
        return None

    def build_rules_for_location(self, extraction_guide: ExtractionGuide) -> Optional[str]:
        """Build rules_for_location field (with title)."""
        rules = self._get_text(extraction_guide.rules_for_location, self.language)
        if rules:
            return self._add_title(rules, "location_rules")
        return None

    def build_model_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build Model/List/Set type Prompt."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules = self.build_rules(extraction_guide)
        if rules:
            parts.append(rules)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_main_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build Graph type main Prompt (single-stage mode)."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(extraction_guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_edges = self.build_rules_for_edges(extraction_guide)
        if rules_for_edges:
            parts.append(rules_for_edges)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_node_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build Graph type node extraction Prompt (two-stage mode)."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(extraction_guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_graph_edge_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build Graph type edge extraction Prompt (two-stage mode)."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules_for_edges = self.build_rules_for_edges(extraction_guide)
        if rules_for_edges:
            parts.append(rules_for_edges)

        known_label = self.labels.get("known_entities", "已知实体")
        parts.append(f"## {known_label}:\n{{known_nodes}}")

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_temporal_graph_node_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build TemporalGraph node extraction Prompt."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(extraction_guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_time = self.build_rules_for_time(extraction_guide)
        if rules_for_time:
            parts.append(rules_for_time)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_spatial_graph_node_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build SpatialGraph node extraction Prompt."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(extraction_guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_location = self.build_rules_for_location(extraction_guide)
        if rules_for_location:
            parts.append(rules_for_location)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)

    def build_spatio_temporal_graph_node_prompt(self, extraction_guide: ExtractionGuide) -> str:
        """Build SpatioTemporalGraph node extraction Prompt."""
        parts = []

        target = self.build_target(extraction_guide)
        if target:
            parts.append(target)

        rules_for_nodes = self.build_rules_for_nodes(extraction_guide)
        if rules_for_nodes:
            parts.append(rules_for_nodes)

        rules_for_time = self.build_rules_for_time(extraction_guide)
        if rules_for_time:
            parts.append(rules_for_time)

        rules_for_location = self.build_rules_for_location(extraction_guide)
        if rules_for_location:
            parts.append(rules_for_location)

        source_label = self.labels.get("source_text", "源文本")
        parts.append(f"## {source_label}:\n{{source_text}}")

        return "\n\n".join(parts)
