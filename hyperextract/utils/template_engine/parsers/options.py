"""Options models and builder."""

from typing import Callable, List, Optional, Type
from pydantic import BaseModel

from ontomem.merger import MergeStrategy

from .output import parse_output
from .identifiers import IdentifierResolver


class Options(BaseModel):
    """Runtime options configuration - excludes LLM, Embedder, Schema, Prompt."""

    merge_strategy: Optional[str] = None
    entity_merge_strategy: Optional[str] = None
    relation_merge_strategy: Optional[str] = None
    extraction_mode: Optional[str] = None
    observation_time: Optional[str] = None
    observation_location: Optional[str] = None
    chunk_size: int = 2048
    chunk_overlap: int = 256
    max_workers: int = 10
    verbose: bool = False
    fields_for_search: Optional[List[str]] = None
    entity_fields_for_search: Optional[List[str]] = None
    relation_fields_for_search: Optional[List[str]] = None

    def get_merge_strategy(self) -> Optional[str]:
        """Get merge strategy."""
        return self.merge_strategy or self.entity_merge_strategy


class ModelOptions:
    """Options for AutoModel."""

    def __init__(
        self,
        merge_strategy: str = "llm_balanced",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        self.merge_strategy = merge_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose


class ListOptions:
    """Options for AutoList."""

    def __init__(
        self,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose


class SetOptions:
    """Options for AutoSet."""

    def __init__(
        self,
        merge_strategy: str = "llm_balanced",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
    ):
        self.merge_strategy = merge_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose


class GraphOptions:
    """Options for AutoGraph/AutoHypergraph."""

    def __init__(
        self,
        extraction_mode: str = "two_stage",
        entity_merge_strategy: str = "llm_balanced",
        relation_merge_strategy: str = "llm_balanced",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        entity_fields_for_search: Optional[List[str]] = None,
        relation_fields_for_search: Optional[List[str]] = None,
    ):
        self.extraction_mode = extraction_mode
        self.entity_merge_strategy = entity_merge_strategy
        self.relation_merge_strategy = relation_merge_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose
        self.entity_fields_for_search = entity_fields_for_search
        self.relation_fields_for_search = relation_fields_for_search


class TemporalGraphOptions(GraphOptions):
    """Options for AutoTemporalGraph."""

    def __init__(
        self,
        extraction_mode: str = "two_stage",
        entity_merge_strategy: str = "llm_balanced",
        relation_merge_strategy: str = "llm_balanced",
        observation_time: Optional[str] = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        entity_fields_for_search: Optional[List[str]] = None,
        relation_fields_for_search: Optional[List[str]] = None,
    ):
        super().__init__(
            extraction_mode=extraction_mode,
            entity_merge_strategy=entity_merge_strategy,
            relation_merge_strategy=relation_merge_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            entity_fields_for_search=entity_fields_for_search,
            relation_fields_for_search=relation_fields_for_search,
        )
        self.observation_time = observation_time


class SpatialGraphOptions(GraphOptions):
    """Options for AutoSpatialGraph."""

    def __init__(
        self,
        extraction_mode: str = "two_stage",
        entity_merge_strategy: str = "llm_balanced",
        relation_merge_strategy: str = "llm_balanced",
        observation_location: Optional[str] = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        entity_fields_for_search: Optional[List[str]] = None,
        relation_fields_for_search: Optional[List[str]] = None,
    ):
        super().__init__(
            extraction_mode=extraction_mode,
            entity_merge_strategy=entity_merge_strategy,
            relation_merge_strategy=relation_merge_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            entity_fields_for_search=entity_fields_for_search,
            relation_fields_for_search=relation_fields_for_search,
        )
        self.observation_location = observation_location


class SpatioTemporalGraphOptions(TemporalGraphOptions):
    """Options for AutoSpatioTemporalGraph."""

    def __init__(
        self,
        extraction_mode: str = "two_stage",
        entity_merge_strategy: str = "llm_balanced",
        relation_merge_strategy: str = "llm_balanced",
        observation_time: Optional[str] = None,
        observation_location: Optional[str] = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        entity_fields_for_search: Optional[List[str]] = None,
        relation_fields_for_search: Optional[List[str]] = None,
    ):
        super().__init__(
            extraction_mode=extraction_mode,
            entity_merge_strategy=entity_merge_strategy,
            relation_merge_strategy=relation_merge_strategy,
            observation_time=observation_time,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            entity_fields_for_search=entity_fields_for_search,
            relation_fields_for_search=relation_fields_for_search,
        )
        self.observation_location = observation_location


class OptionsBuilder:
    """Options Builder - handles option parsing, validation, merge strategy resolution."""

    @staticmethod
    def get_language(config) -> str:
        """Get language setting."""
        lang = config.language
        if isinstance(lang, list):
            return lang[0] if lang else "zh"
        return lang or "zh"

    @staticmethod
    def get_extraction_mode(config) -> str:
        """Get extraction mode."""
        return config.options.extraction_mode if config.options else "two_stage"

    VALID_MERGE_STRATEGIES = {
        "merge_field",
        "keep_incoming",
        "keep_existing",
        "llm_balanced",
        "llm_prefer_incoming",
        "llm_prefer_existing",
    }

    @staticmethod
    def resolve_merge_strategy(
        strategy_name: Optional[str],
        key_extractor: Callable,
        llm_client,
        item_schema: Type,
    ):
        """Resolve merge strategy."""
        if strategy_name:
            strategy_name = strategy_name.lower()
            if strategy_name not in OptionsBuilder.VALID_MERGE_STRATEGIES:
                raise ValueError(
                    f"Invalid merge strategy '{strategy_name}'. "
                    f"Valid options: {OptionsBuilder.VALID_MERGE_STRATEGIES}"
                )
            # 处理下划线格式，转换为点格式
            if '_' in strategy_name and '.' not in strategy_name:
                parts = strategy_name.split('_')
                if len(parts) == 2 and parts[0] in ['llm']:
                    return getattr(getattr(MergeStrategy, parts[0].upper()), parts[1].upper())
            elif '.' in strategy_name:
                parts = strategy_name.split('.')
                return getattr(getattr(MergeStrategy, parts[0].upper()), parts[1].upper())
            else:
                return MergeStrategy[strategy_name.upper()]
        return MergeStrategy.LLM.BALANCED

    @classmethod
    def build_model_options(cls, config):
        """Build options for AutoModel."""
        options = config.options or Options()
        return ModelOptions(
            merge_strategy=options.merge_strategy or "llm_balanced",
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
        )

    @classmethod
    def build_list_options(cls, config):
        """Build options for AutoList."""
        options = config.options or Options()
        return ListOptions(
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
        )

    @classmethod
    def build_set_options(cls, config):
        """Build options for AutoSet."""
        options = config.options or Options()
        return SetOptions(
            merge_strategy=options.merge_strategy or "llm_balanced",
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
        )

    @classmethod
    def build_graph_options(cls, config):
        """Build options for AutoGraph/AutoHypergraph."""
        options = config.options or Options()
        extraction_mode = cls.get_extraction_mode(config)
        return GraphOptions(
            extraction_mode=extraction_mode,
            entity_merge_strategy=options.entity_merge_strategy or "llm_balanced",
            relation_merge_strategy=options.relation_merge_strategy or "llm_balanced",
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_search=options.entity_fields_for_search,
            relation_fields_for_search=options.relation_fields_for_search,
        )

    @classmethod
    def build_temporal_graph_options(cls, config):
        """Build options for AutoTemporalGraph."""
        options = config.options or Options()
        extraction_mode = cls.get_extraction_mode(config)
        return TemporalGraphOptions(
            extraction_mode=extraction_mode,
            entity_merge_strategy=options.entity_merge_strategy or "llm_balanced",
            relation_merge_strategy=options.relation_merge_strategy or "llm_balanced",
            observation_time=options.observation_time,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_search=options.entity_fields_for_search,
            relation_fields_for_search=options.relation_fields_for_search,
        )

    @classmethod
    def build_spatial_graph_options(cls, config):
        """Build options for AutoSpatialGraph."""
        options = config.options or Options()
        extraction_mode = cls.get_extraction_mode(config)
        return SpatialGraphOptions(
            extraction_mode=extraction_mode,
            entity_merge_strategy=options.entity_merge_strategy or "llm_balanced",
            relation_merge_strategy=options.relation_merge_strategy or "llm_balanced",
            observation_location=options.observation_location,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_search=options.entity_fields_for_search,
            relation_fields_for_search=options.relation_fields_for_search,
        )

    @classmethod
    def build_spatio_temporal_graph_options(cls, config):
        """Build options for AutoSpatioTemporalGraph."""
        options = config.options or Options()
        extraction_mode = cls.get_extraction_mode(config)
        return SpatioTemporalGraphOptions(
            extraction_mode=extraction_mode,
            entity_merge_strategy=options.entity_merge_strategy or "llm_balanced",
            relation_merge_strategy=options.relation_merge_strategy or "llm_balanced",
            observation_time=options.observation_time,
            observation_location=options.observation_location,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_search=options.entity_fields_for_search,
            relation_fields_for_search=options.relation_fields_for_search,
        )

    @classmethod
    def validate_model_config(cls, config):
        """Validate AutoModel configuration."""
        schema_dict = parse_output(config)
        if schema_dict.get("schema") is None:
            raise ValueError(f"AutoModel requires schema definition: {config.name}")
        return schema_dict

    @classmethod
    def validate_list_config(cls, config):
        """Validate AutoList configuration."""
        schema_dict = parse_output(config)
        if schema_dict.get("item_schema") is None:
            raise ValueError(f"AutoList requires item_schema definition: {config.name}")
        return schema_dict

    @classmethod
    def validate_set_config(cls, config):
        """Validate AutoSet configuration."""
        schema_dict = parse_output(config)
        if schema_dict.get("item_schema") is None:
            raise ValueError(f"AutoSet requires item_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        if identifiers.get("item_id_extractor") is None:
            raise ValueError(f"AutoSet requires item_id configuration: {config.name}")

        return schema_dict, identifiers

    @classmethod
    def validate_graph_config(cls, config):
        """Validate AutoGraph/AutoHypergraph configuration."""
        schema_dict = parse_output(config)
        if schema_dict.get("entity_schema") is None or schema_dict.get("relation_schema") is None:
            raise ValueError(f"AutoGraph requires entity_schema and relation_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        required = ["entity_key_extractor", "relation_key_extractor", "entities_in_relation_extractor"]
        if not all(identifiers.get(k) for k in required):
            raise ValueError(f"AutoGraph requires complete identifiers configuration: {config.name}")

        return schema_dict, identifiers

    @classmethod
    def validate_temporal_graph_config(cls, config):
        """Validate AutoTemporalGraph configuration."""
        schema_dict, identifiers = cls.validate_graph_config(config)

        if identifiers.get("time_in_relation_extractor") is None:
            raise ValueError(f"AutoTemporalGraph requires time_field in identifiers: {config.name}")

        return schema_dict, identifiers

    @classmethod
    def validate_spatial_graph_config(cls, config):
        """Validate AutoSpatialGraph configuration."""
        schema_dict, identifiers = cls.validate_graph_config(config)

        if identifiers.get("location_in_relation_extractor") is None:
            raise ValueError(f"AutoSpatialGraph requires location_field in identifiers: {config.name}")

        return schema_dict, identifiers

    @classmethod
    def validate_spatio_temporal_graph_config(cls, config):
        """Validate AutoSpatioTemporalGraph configuration."""
        schema_dict, identifiers = cls.validate_graph_config(config)

        if not identifiers.get("time_in_relation_extractor") or not identifiers.get("location_in_relation_extractor"):
            raise ValueError(f"AutoSpatioTemporalGraph requires time_field and location_field in identifiers: {config.name}")

        return schema_dict, identifiers


__all__ = [
    "Options",
    "ModelOptions",
    "ListOptions",
    "SetOptions",
    "GraphOptions",
    "TemporalGraphOptions",
    "SpatialGraphOptions",
    "SpatioTemporalGraphOptions",
    "OptionsBuilder",
]
