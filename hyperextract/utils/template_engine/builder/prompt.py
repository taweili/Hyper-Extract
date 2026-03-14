"""Extraction models and prompt builder."""

from typing import Tuple
from .tools import get_text, TemplateSchema, GuidelineSchema


__all__ = [
    "PromptParser",
]


LABEL_MAPPING = {
    "zh": {
        "role_and_task": "角色与任务",
        "source_text": "源文本",
        "known_entities": "已知实体",
        "extraction_rules": "提取规则",
        "entity_rules": "实体提取规则",
        "relation_rules": "关系提取规则",
        "time_rules": "时间规则",
        "location_rules": "位置规则",
    },
    "en": {
        "role_and_task": "Role and Task",
        "source_text": "Source Text",
        "known_entities": "Known Entities",
        "extraction_rules": "Extraction Rules",
        "entity_rules": "Entity Extraction Rules",
        "relation_rules": "Relation Extraction Rules",
        "time_rules": "Time Rules",
        "location_rules": "Location Rules",
    },
}


def PromptParser(
    template: TemplateSchema, language: str = "en"
) -> Tuple[str, str, str]:
    """Parse template and return prompts based on autotype.

    Args:
        template: Template Configuration instance
        language: Language code (default: "en")

    Returns:
        tuple: main_prompt or (main_prompt, node_prompt, edge_prompt)
        - For non-graph types: returns main_prompt
        - For graph types in two_stage mode: returns (main_prompt, node_prompt, edge_prompt)
    """
    labels = LABEL_MAPPING.get(language, LABEL_MAPPING["zh"])
    autotype = template.type
    guideline: GuidelineSchema = template.guideline

    prefix_prompt = (
        f"# {labels.get('role_and_task')}:\n{get_text(guideline.target, language)}"
    )

    if autotype in ("model", "list", "set"):
        parts = [prefix_prompt]
        parts.append(
            f"## {labels.get('extraction_rules')}:\n{get_text(guideline.rules, language)}"
        )
        parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")
        return "\n\n".join(parts)
    else:
        # main prompt
        main_parts = [prefix_prompt]
        main_parts.append(
            f"## {labels.get('entity_rules')}:\n{get_text(guideline.rules, language)}"
        )
        main_parts.append(
            f"## {labels.get('relation_rules')}:\n{get_text(guideline.rules_for_relations, language)}"
        )
        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            main_parts.append(
                f"## {labels.get('time_rules')}:\n{get_text(guideline.rules_for_time, language)}"
            )
        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            main_parts.append(
                f"## {labels.get('location_rules')}:\n{get_text(guideline.rules_for_location, language)}"
            )
        main_parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")

        # node prompt
        node_parts = [prefix_prompt]
        node_parts.append(
            f"## {labels.get('entity_rules')}:\n{get_text(guideline.rules, language)}"
        )
        node_parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")

        # edge prompt
        edge_parts = [prefix_prompt]
        edge_parts.append(
            f"## {labels.get('relation_rules')}:\n{get_text(guideline.rules_for_relations, language)}"
        )
        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            edge_parts.append(
                f"## {labels.get('time_rules')}:\n{get_text(guideline.rules_for_time, language)}"
            )
        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            edge_parts.append(
                f"## {labels.get('location_rules')}:\n{get_text(guideline.rules_for_location, language)}"
            )
        edge_parts.append(f"## {labels.get('known_entities')}:\n{{known_nodes}}")
        edge_parts.append(f"## {labels.get('source_text')}:\n{{source_text}}")

        return "\n\n".join(main_parts), "\n\n".join(node_parts), "\n\n".join(edge_parts)
