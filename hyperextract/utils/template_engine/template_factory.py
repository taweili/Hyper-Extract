"""Template Factory - Dynamically creates template instances from configuration.

Supports all 8 AutoType dynamic generation.
"""

from typing import Any, Callable, Dict, List, Optional, Type, Union
from pathlib import Path

from ontomem.merger import MergeStrategy, create_merger, BaseMerger
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from hyperextract.types import (
    AutoModel,
    AutoList,
    AutoSet,
    AutoGraph,
    AutoHypergraph,
    AutoTemporalGraph,
    AutoSpatialGraph,
    AutoSpatioTemporalGraph,
)

from .config_loader import TemplateConfig, Parameters
from .schema_builder import SchemaBuilder
from .identifier_resolver import IdentifierResolver
from .prompt_builder import PromptBuilder


class TemplateFactory:

    @staticmethod
    def get_language(config: TemplateConfig) -> str:
        """Get language setting."""
        lang = config.language
        if isinstance(lang, list):
            return lang[0] if lang else "zh"
        return lang or "zh"

    @staticmethod
    def resolve_display_extractors(config: TemplateConfig, schema_dict: dict):
        """Generate label_extractor function based on display configuration."""
        display = config.display
        if not display:
            return {}

        result = {}
        autotype = config.autotype
        display_dict = display.model_dump() if hasattr(display, 'model_dump') else display

        if autotype in ("model", "list", "set"):
            label_field = display_dict.get("label")
            if label_field:
                result["label_extractor"] = lambda x: str(getattr(x, label_field, ""))

        elif autotype in ("graph", "hypergraph", "temporal_graph", "spatial_graph", "spatio_temporal_graph"):
            node_label_field = display_dict.get("node_label")
            if node_label_field:
                result["node_label_extractor"] = lambda x: str(getattr(x, node_label_field, ""))

            edge_label_field = display_dict.get("edge_label")
            if edge_label_field:
                result["edge_label_extractor"] = lambda x: str(getattr(x, edge_label_field, ""))

        return result

    @staticmethod
    def resolve_merge_strategy(
        strategy_name: Optional[str],
        custom_rule: Optional[str],
        key_extractor: Callable,
        llm_client: BaseChatModel,
        item_schema: Type,
    ) -> Union[MergeStrategy, BaseMerger]:
        """Resolve merge strategy."""
        if custom_rule:
            return MergeStrategy.LLM.BALANCED
        if strategy_name:
            strategy_name = strategy_name.lower()
            if '.' in strategy_name:
                parts = strategy_name.split('.')
                return getattr(getattr(MergeStrategy, parts[0].upper()), parts[1].upper())
            else:
                try:
                    return MergeStrategy[strategy_name.upper()]
                except KeyError:
                    return MergeStrategy.LLM.BALANCED
        return MergeStrategy.LLM.BALANCED

    @classmethod
    def create_model(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoModel:
        """Create AutoModel template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        schema_class = schema_dict.get("schema")

        if schema_class is None:
            raise ValueError(f"AutoModel requires schema definition: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)
        prompt = prompt_builder.build_model_prompt(extraction_guide)

        parameters = config.parameters or Parameters()
        merge_strategy = parameters.merge_strategy or "llm_balanced"
        custom_merge_rule = parameters.get_custom_merge_rule(language)

        return AutoModel(
            data_schema=schema_class,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=cls.resolve_merge_strategy(
                merge_strategy,
                custom_merge_rule,
                lambda x: str(x),
                llm_client,
                schema_class,
            ),
            prompt=prompt,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
        )

    @classmethod
    def create_list(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoList:
        """Create AutoList template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        item_schema_class = schema_dict.get("item_schema")

        if item_schema_class is None:
            raise ValueError(f"AutoList requires item_schema definition: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)
        prompt = prompt_builder.build_model_prompt(extraction_guide)

        parameters = config.parameters or Parameters()

        return AutoList(
            item_schema=item_schema_class,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
        )

    @classmethod
    def create_set(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoSet:
        """Create AutoSet template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        item_schema_class = schema_dict.get("item_schema")

        if item_schema_class is None:
            raise ValueError(f"AutoSet requires item_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        item_id_extractor = identifiers.get("item_id_extractor")

        if item_id_extractor is None:
            raise ValueError(f"AutoSet requires item_id configuration: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)
        prompt = prompt_builder.build_model_prompt(extraction_guide)

        parameters = config.parameters or Parameters()
        merge_strategy = parameters.merge_strategy or "llm_balanced"
        custom_merge_rule = parameters.get_custom_merge_rule(language)

        return AutoSet(
            item_schema=item_schema_class,
            item_key_extractor=item_id_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=cls.resolve_merge_strategy(
                merge_strategy,
                custom_merge_rule,
                item_id_extractor,
                llm_client,
                item_schema_class,
            ),
            prompt=prompt,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
        )

    @classmethod
    def create_graph(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoGraph:
        """Create AutoGraph template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        node_schema_class = schema_dict.get("node_schema")
        edge_schema_class = schema_dict.get("edge_schema")

        if node_schema_class is None or edge_schema_class is None:
            raise ValueError(f"AutoGraph requires node_schema and edge_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        node_key_extractor = identifiers.get("node_key_extractor")
        edge_key_extractor = identifiers.get("edge_key_extractor")
        nodes_in_edge_extractor = identifiers.get("nodes_in_edge_extractor")

        if not all([node_key_extractor, edge_key_extractor, nodes_in_edge_extractor]):
            raise ValueError(f"AutoGraph requires complete identifiers configuration: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)

        extraction_mode = config.parameters.extraction_mode if config.parameters else "two_stage"

        if extraction_mode == "one_stage":
            prompt = prompt_builder.build_graph_main_prompt(extraction_guide)
            prompt_for_node_extraction = ""
            prompt_for_edge_extraction = ""
        else:
            prompt = ""
            prompt_for_node_extraction = prompt_builder.build_graph_node_prompt(extraction_guide)
            prompt_for_edge_extraction = prompt_builder.build_graph_edge_prompt(extraction_guide)

        parameters = config.parameters or Parameters()

        node_merge_strategy = parameters.node_merge_strategy or "llm_balanced"
        node_custom_merge_rule = parameters.node_custom_merge_rule
        edge_merge_strategy = parameters.edge_merge_strategy or "llm_balanced"
        edge_custom_merge_rule = parameters.edge_custom_merge_rule

        return AutoGraph(
            node_schema=node_schema_class,
            edge_schema=edge_schema_class,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            node_strategy_or_merger=cls.resolve_merge_strategy(
                node_merge_strategy,
                node_custom_merge_rule,
                node_key_extractor,
                llm_client,
                node_schema_class,
            ),
            edge_strategy_or_merger=cls.resolve_merge_strategy(
                edge_merge_strategy,
                edge_custom_merge_rule,
                edge_key_extractor,
                llm_client,
                edge_schema_class,
            ),
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_node_extraction,
            prompt_for_edge_extraction=prompt_for_edge_extraction,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
            node_fields_for_index=parameters.node_search_fields,
            edge_fields_for_index=parameters.edge_search_fields,
        )

    @classmethod
    def create_hypergraph(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoHypergraph:
        """Create AutoHypergraph template."""
        return cls.create_graph(config, llm_client, embedder)

    @classmethod
    def create_temporal_graph(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoTemporalGraph:
        """Create AutoTemporalGraph template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        node_schema_class = schema_dict.get("node_schema")
        edge_schema_class = schema_dict.get("edge_schema")

        if node_schema_class is None or edge_schema_class is None:
            raise ValueError(f"AutoTemporalGraph requires node_schema and edge_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        node_key_extractor = identifiers.get("node_key_extractor")
        edge_key_extractor = identifiers.get("edge_key_extractor")
        nodes_in_edge_extractor = identifiers.get("nodes_in_edge_extractor")
        time_in_edge_extractor = identifiers.get("time_in_edge_extractor")

        if not all([node_key_extractor, edge_key_extractor, nodes_in_edge_extractor]):
            raise ValueError(f"AutoTemporalGraph requires complete identifiers configuration: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)

        extraction_mode = config.parameters.extraction_mode if config.parameters else "two_stage"

        if extraction_mode == "one_stage":
            prompt = prompt_builder.build_graph_main_prompt(extraction_guide)
            prompt_for_node_extraction = ""
            prompt_for_edge_extraction = ""
        else:
            prompt = ""
            prompt_for_node_extraction = prompt_builder.build_temporal_graph_node_prompt(extraction_guide)
            prompt_for_edge_extraction = prompt_builder.build_graph_edge_prompt(extraction_guide)

        parameters = config.parameters or Parameters()

        node_merge_strategy = parameters.node_merge_strategy or "llm_balanced"
        node_custom_merge_rule = parameters.node_custom_merge_rule
        edge_merge_strategy = parameters.edge_merge_strategy or "llm_balanced"
        edge_custom_merge_rule = parameters.edge_custom_merge_rule

        return AutoTemporalGraph(
            node_schema=node_schema_class,
            edge_schema=edge_schema_class,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            time_in_edge_extractor=time_in_edge_extractor,
            observation_time=parameters.observation_time,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            node_strategy_or_merger=cls.resolve_merge_strategy(
                node_merge_strategy,
                node_custom_merge_rule,
                node_key_extractor,
                llm_client,
                node_schema_class,
            ),
            edge_strategy_or_merger=cls.resolve_merge_strategy(
                edge_merge_strategy,
                edge_custom_merge_rule,
                edge_key_extractor,
                llm_client,
                edge_schema_class,
            ),
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_node_extraction,
            prompt_for_edge_extraction=prompt_for_edge_extraction,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
            node_fields_for_index=parameters.node_search_fields,
            edge_fields_for_index=parameters.edge_search_fields,
        )

    @classmethod
    def create_spatial_graph(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoSpatialGraph:
        """Create AutoSpatialGraph template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        node_schema_class = schema_dict.get("node_schema")
        edge_schema_class = schema_dict.get("edge_schema")

        if node_schema_class is None or edge_schema_class is None:
            raise ValueError(f"AutoSpatialGraph requires node_schema and edge_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        node_key_extractor = identifiers.get("node_key_extractor")
        edge_key_extractor = identifiers.get("edge_key_extractor")
        nodes_in_edge_extractor = identifiers.get("nodes_in_edge_extractor")
        location_extractor = identifiers.get("location_extractor")

        if not all([node_key_extractor, edge_key_extractor, nodes_in_edge_extractor]):
            raise ValueError(f"AutoSpatialGraph requires complete identifiers configuration: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)

        extraction_mode = config.parameters.extraction_mode if config.parameters else "two_stage"

        if extraction_mode == "one_stage":
            prompt = prompt_builder.build_graph_main_prompt(extraction_guide)
            prompt_for_node_extraction = ""
            prompt_for_edge_extraction = ""
        else:
            prompt = ""
            prompt_for_node_extraction = prompt_builder.build_spatial_graph_node_prompt(extraction_guide)
            prompt_for_edge_extraction = prompt_builder.build_graph_edge_prompt(extraction_guide)

        parameters = config.parameters or Parameters()

        node_merge_strategy = parameters.node_merge_strategy or "llm_balanced"
        node_custom_merge_rule = parameters.node_custom_merge_rule
        edge_merge_strategy = parameters.edge_merge_strategy or "llm_balanced"
        edge_custom_merge_rule = parameters.edge_custom_merge_rule

        return AutoSpatialGraph(
            node_schema=node_schema_class,
            edge_schema=edge_schema_class,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            location_extractor=location_extractor,
            observation_location=parameters.observation_location,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            node_strategy_or_merger=cls.resolve_merge_strategy(
                node_merge_strategy,
                node_custom_merge_rule,
                node_key_extractor,
                llm_client,
                node_schema_class,
            ),
            edge_strategy_or_merger=cls.resolve_merge_strategy(
                edge_merge_strategy,
                edge_custom_merge_rule,
                edge_key_extractor,
                llm_client,
                edge_schema_class,
            ),
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_node_extraction,
            prompt_for_edge_extraction=prompt_for_edge_extraction,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
            node_fields_for_index=parameters.node_search_fields,
            edge_fields_for_index=parameters.edge_search_fields,
        )

    @classmethod
    def create_spatio_temporal_graph(cls, config: TemplateConfig, llm_client: BaseChatModel, embedder: Embeddings) -> AutoSpatioTemporalGraph:
        """Create AutoSpatioTemporalGraph template."""
        language = cls.get_language(config)

        schema_dict = SchemaBuilder.build_schema(config)
        node_schema_class = schema_dict.get("node_schema")
        edge_schema_class = schema_dict.get("edge_schema")

        if node_schema_class is None or edge_schema_class is None:
            raise ValueError(f"AutoSpatioTemporalGraph requires node_schema and edge_schema definition: {config.name}")

        identifiers = IdentifierResolver.resolve_all(config)
        node_key_extractor = identifiers.get("node_key_extractor")
        edge_key_extractor = identifiers.get("edge_key_extractor")
        nodes_in_edge_extractor = identifiers.get("nodes_in_edge_extractor")
        time_extractor = identifiers.get("time_extractor")
        location_extractor = identifiers.get("location_extractor")

        if not all([node_key_extractor, edge_key_extractor, nodes_in_edge_extractor]):
            raise ValueError(f"AutoSpatioTemporalGraph requires complete identifiers configuration: {config.name}")

        extraction_guide = config.extraction_guide
        prompt_builder = PromptBuilder(language)

        extraction_mode = config.parameters.extraction_mode if config.parameters else "two_stage"

        if extraction_mode == "one_stage":
            prompt = prompt_builder.build_graph_main_prompt(extraction_guide)
            prompt_for_node_extraction = ""
            prompt_for_edge_extraction = ""
        else:
            prompt = ""
            prompt_for_node_extraction = prompt_builder.build_spatio_temporal_graph_node_prompt(extraction_guide)
            prompt_for_edge_extraction = prompt_builder.build_graph_edge_prompt(extraction_guide)

        parameters = config.parameters or Parameters()

        node_merge_strategy = parameters.node_merge_strategy or "llm_balanced"
        node_custom_merge_rule = parameters.node_custom_merge_rule
        edge_merge_strategy = parameters.edge_merge_strategy or "llm_balanced"
        edge_custom_merge_rule = parameters.edge_custom_merge_rule

        return AutoSpatioTemporalGraph(
            node_schema=node_schema_class,
            edge_schema=edge_schema_class,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            time_extractor=time_extractor,
            location_extractor=location_extractor,
            observation_time=parameters.observation_time,
            observation_location=parameters.observation_location,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            node_strategy_or_merger=cls.resolve_merge_strategy(
                node_merge_strategy,
                node_custom_merge_rule,
                node_key_extractor,
                llm_client,
                node_schema_class,
            ),
            edge_strategy_or_merger=cls.resolve_merge_strategy(
                edge_merge_strategy,
                edge_custom_merge_rule,
                edge_key_extractor,
                llm_client,
                edge_schema_class,
            ),
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_node_extraction,
            prompt_for_edge_extraction=prompt_for_edge_extraction,
            chunk_size=parameters.chunk_size,
            chunk_overlap=parameters.chunk_overlap,
            max_workers=parameters.max_workers,
            verbose=parameters.verbose,
            node_fields_for_index=parameters.node_search_fields,
            edge_fields_for_index=parameters.edge_search_fields,
        )

    @classmethod
    def create(
        cls,
        config: TemplateConfig,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs
    ):
        """Create template instance based on configuration.

        Args:
            config: Template configuration
            llm_client: LLM client
            embedder: Embedding model
            **kwargs: Additional parameters to override config parameters
                e.g., observation_time="2024-06-15", observation_location="Beijing"

        Returns:
            TemplateWrapper: Wrapped template instance

        Examples:
            # Basic usage
            template = TemplateFactory.create(config, llm, embedder)

            # For spatio-temporal templates, pass observation_time etc.
            template = TemplateFactory.create(
                config,
                llm,
                embedder,
                observation_time="2024-06-15",
                observation_location="Beijing"
            )

            # Can also override other parameters
            template = TemplateFactory.create(
                config,
                llm,
                embedder,
                chunk_size=4096,
                max_workers=20
            )
        """
        # Merge parameters: user-provided kwargs have highest priority
        if kwargs:
            from .config_loader import Parameters
            base_params = config.parameters or Parameters()
            params_dict = base_params.model_dump()
            params_dict.update(kwargs)
            config.parameters = Parameters(**params_dict)

        autotype_map = {
            "model": cls.create_model,
            "list": cls.create_list,
            "set": cls.create_set,
            "graph": cls.create_graph,
            "hypergraph": cls.create_hypergraph,
            "temporal_graph": cls.create_temporal_graph,
            "spatial_graph": cls.create_spatial_graph,
            "spatio_temporal_graph": cls.create_spatio_temporal_graph,
        }

        creator = autotype_map.get(config.autotype)
        if creator is None:
            raise ValueError(f"Unsupported autotype: {config.autotype}")

        template = creator(config, llm_client, embedder)
        display_extractors = cls.resolve_display_extractors(config, {})

        return TemplateWrapper(template, display_extractors, config.autotype)


def safe_getattr(obj, name, default):
    """Safely get attribute."""
    try:
        return getattr(obj, name)
    except AttributeError:
        return default


class TemplateWrapper:
    """Template wrapper - automatically handles label_extractor parameters."""

    def __init__(self, template, display_extractors: dict, autotype: str = None):
        self._template = template
        self._display_extractors = display_extractors
        self._autotype = autotype

        self._node_label_extractor = display_extractors.get("node_label_extractor")
        self._edge_label_extractor = display_extractors.get("edge_label_extractor")
        self._label_extractor = display_extractors.get("label_extractor")

    def __getattr__(self, name):
        return getattr(self._template, name)

    def show(self, **kwargs):
        """Automatically pass label_extractor parameters."""
        if self._autotype in ("graph", "hypergraph", "temporal_graph", "spatial_graph", "spatio_temporal_graph"):
            if self._node_label_extractor and self._edge_label_extractor:
                kwargs.setdefault("node_label_extractor", self._node_label_extractor)
                kwargs.setdefault("edge_label_extractor", self._edge_label_extractor)
        else:
            if self._label_extractor:
                kwargs.setdefault("label_extractor", self._label_extractor)

        return self._template.show(**kwargs)

    def search(self, **kwargs):
        return self._template.search(**kwargs)

    def chat(self, **kwargs):
        return self._template.chat(**kwargs)
