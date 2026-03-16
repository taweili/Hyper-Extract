"""Template Factory - Dynamically creates template instances from configuration.

Supports all 8 AutoType dynamic generation.
"""

from typing import TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .parsers import (
    TemplateCfg,
    Options,
    parse_output,
    IdentifierResolver,
    parse_guideline,
    localize_template,
    parse_option,
)


if TYPE_CHECKING:
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


class TemplateFactory:
    @staticmethod
    def resolve_display_extractors(config: TemplateCfg, schema_dict: dict = None):
        """Generate label_extractor function based on display configuration."""
        display = config.display
        if not display:
            return {}

        result = {}
        autotype = config.type
        display_dict = (
            display.model_dump() if hasattr(display, "model_dump") else display
        )

        if autotype in ("model", "list", "set"):
            label_field = display_dict.get("label")
            if label_field:
                result["label_extractor"] = lambda x: str(getattr(x, label_field, ""))

        elif autotype in (
            "graph",
            "hypergraph",
            "temporal_graph",
            "spatial_graph",
            "spatio_temporal_graph",
        ):
            entity_label_field = display_dict.get("entity_label")
            if entity_label_field:
                result["entity_label_extractor"] = lambda x: str(
                    getattr(x, entity_label_field, "")
                )

            relation_label_field = display_dict.get("relation_label")
            if relation_label_field:
                result["relation_label_extractor"] = lambda x: str(
                    getattr(x, relation_label_field, "")
                )

        return result

    @classmethod
    def create_model(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoModel":
        """Create AutoModel template."""
        from hyperextract.types import AutoModel

        data_schema = parse_output(config)

        prompt, _, _ = parse_guideline(config.guideline, config.type)

        options = OptionsBuilder.build_model_options(config)

        return AutoModel(
            data_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
        )

    @classmethod
    def create_list(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoList":
        """Create AutoList template."""
        from hyperextract.types import AutoList

        data_schema = parse_output(config)

        prompt, _, _ = parse_guideline(config.guideline, config.type)

        options = OptionsBuilder.build_list_options(config)

        return AutoList(
            item_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
        )

    @classmethod
    def create_set(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoSet":
        """Create AutoSet template."""
        from hyperextract.types import AutoSet

        data_schema = parse_output(config)
        identifiers = IdentifierResolver.resolve_all(config)
        item_id_extractor = identifiers.get("item_id_extractor")

        prompt, _, _ = parse_guideline(config.guideline, config.type)

        options = OptionsBuilder.build_set_options(config)

        return AutoSet(
            item_schema=data_schema,
            item_key_extractor=item_id_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.merge_strategy,
                item_id_extractor,
                llm_client,
                data_schema,
            ),
            prompt=prompt,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
        )

    @classmethod
    def create_graph(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoGraph":
        """Create AutoGraph template."""
        from hyperextract.types import AutoGraph

        entity_schema, relation_schema = parse_output(config)
        identifiers = IdentifierResolver.resolve_all(config)
        entity_key_extractor = identifiers.get("entity_key_extractor")
        relation_key_extractor = identifiers.get("relation_key_extractor")
        entities_in_relation_extractor = identifiers.get(
            "entities_in_relation_extractor"
        )

        options = OptionsBuilder.build_graph_options(config)

        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )

        return AutoGraph(
            entity_schema=entity_schema,
            relation_schema=relation_schema,
            entity_key_extractor=entity_key_extractor,
            relation_key_extractor=relation_key_extractor,
            entities_in_relation_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=options.extraction_mode,
            entity_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.entity_merge_strategy,
                entity_key_extractor,
                llm_client,
                entity_schema,
            ),
            relation_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.relation_merge_strategy,
                relation_key_extractor,
                llm_client,
                relation_schema,
            ),
            prompt=prompt,
            prompt_for_entity_extraction=prompt_for_entity_extraction,
            prompt_for_relation_extraction=prompt_for_relation_extraction,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_index=options.entity_fields_for_search,
            relation_fields_for_index=options.relation_fields_for_search,
        )

    @classmethod
    def create_hypergraph(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoHypergraph":
        return cls.create_graph(config, llm_client, embedder)

    @classmethod
    def create_temporal_graph(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoTemporalGraph":
        from hyperextract.types import AutoTemporalGraph

        entity_schema, relation_schema = parse_output(config)
        identifiers = IdentifierResolver.resolve_all(config)
        entity_key_extractor = identifiers.get("entity_key_extractor")
        relation_key_extractor = identifiers.get("relation_key_extractor")
        entities_in_relation_extractor = identifiers.get(
            "entities_in_relation_extractor"
        )
        time_in_relation_extractor = identifiers.get("time_in_relation_extractor")

        options = OptionsBuilder.build_temporal_graph_options(config)

        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )

        return AutoTemporalGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            time_in_edge_extractor=time_in_relation_extractor,
            observation_time=options.observation_time,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=options.extraction_mode,
            node_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.entity_merge_strategy,
                entity_key_extractor,
                llm_client,
                entity_schema,
            ),
            edge_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.relation_merge_strategy,
                relation_key_extractor,
                llm_client,
                relation_schema,
            ),
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            node_fields_for_index=options.entity_fields_for_search,
            edge_fields_for_index=options.relation_fields_for_search,
        )

    @classmethod
    def create_spatial_graph(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoSpatialGraph":
        from hyperextract.types import AutoSpatialGraph

        entity_schema, relation_schema = parse_output(config)
        identifiers = IdentifierResolver.resolve_all(config)
        entity_key_extractor = identifiers.get("entity_key_extractor")
        relation_key_extractor = identifiers.get("relation_key_extractor")
        entities_in_relation_extractor = identifiers.get(
            "entities_in_relation_extractor"
        )
        location_in_relation_extractor = identifiers.get(
            "location_in_relation_extractor"
        )

        options = OptionsBuilder.build_spatial_graph_options(config)

        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )

        return AutoSpatialGraph(
            entity_schema=entity_schema,
            relation_schema=relation_schema,
            entity_key_extractor=entity_key_extractor,
            relation_key_extractor=relation_key_extractor,
            entities_in_relation_extractor=entities_in_relation_extractor,
            location_in_relation_extractor=location_in_relation_extractor,
            observation_location=options.observation_location,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=options.extraction_mode,
            entity_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.entity_merge_strategy,
                entity_key_extractor,
                llm_client,
                entity_schema,
            ),
            relation_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.relation_merge_strategy,
                relation_key_extractor,
                llm_client,
                relation_schema,
            ),
            prompt=prompt,
            prompt_for_entity_extraction=prompt_for_entity_extraction,
            prompt_for_relation_extraction=prompt_for_relation_extraction,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_index=options.entity_fields_for_search,
            relation_fields_for_index=options.relation_fields_for_search,
        )

    @classmethod
    def create_spatio_temporal_graph(
        cls, config: TemplateCfg, llm_client: BaseChatModel, embedder: Embeddings
    ) -> "AutoSpatioTemporalGraph":
        from hyperextract.types import AutoSpatioTemporalGraph

        entity_schema, relation_schema = parse_output(config)
        identifiers = IdentifierResolver.resolve_all(config)
        entity_key_extractor = identifiers.get("entity_key_extractor")
        relation_key_extractor = identifiers.get("relation_key_extractor")
        entities_in_relation_extractor = identifiers.get(
            "entities_in_relation_extractor"
        )
        time_in_relation_extractor = identifiers.get("time_in_relation_extractor")
        location_in_relation_extractor = identifiers.get(
            "location_in_relation_extractor"
        )

        options = OptionsBuilder.build_spatio_temporal_graph_options(config)

        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )

        return AutoSpatioTemporalGraph(
            entity_schema=entity_schema,
            relation_schema=relation_schema,
            entity_key_extractor=entity_key_extractor,
            relation_key_extractor=relation_key_extractor,
            entities_in_relation_extractor=entities_in_relation_extractor,
            time_in_relation_extractor=time_in_relation_extractor,
            location_in_relation_extractor=location_in_relation_extractor,
            observation_time=options.observation_time,
            observation_location=options.observation_location,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=options.extraction_mode,
            entity_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.entity_merge_strategy,
                entity_key_extractor,
                llm_client,
                entity_schema,
            ),
            relation_strategy_or_merger=OptionsBuilder.resolve_merge_strategy(
                options.relation_merge_strategy,
                relation_key_extractor,
                llm_client,
                relation_schema,
            ),
            prompt=prompt,
            prompt_for_entity_extraction=prompt_for_entity_extraction,
            prompt_for_relation_extraction=prompt_for_relation_extraction,
            chunk_size=options.chunk_size,
            chunk_overlap=options.chunk_overlap,
            max_workers=options.max_workers,
            verbose=options.verbose,
            entity_fields_for_index=options.entity_fields_for_search,
            relation_fields_for_index=options.relation_fields_for_search,
        )

    @classmethod
    def create(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        language: str = "zh",
        **kwargs,
    ):
        """Create template instance based on configuration.

        Args:
            config: Template configuration
            llm_client: LLM client
            embedder: Embedding model
            language: Language code for localization (e.g., 'zh', 'en')
            **kwargs: Additional parameters to override config parameters
                e.g., observation_time="2024-06-15", observation_location="Beijing"

        Returns:
            TemplateWrapper: Wrapped template instance

        Examples:
            # Basic usage
            template = TemplateFactory.create(config, llm, embedder)

            # For specific language
            template = TemplateFactory.create(config, llm, embedder, language="en")

            # For spatio-temporal templates, pass observation_time etc.
            template = TemplateFactory.create(
                config,
                llm,
                embedder,
                language="zh",
                observation_time="2024-06-15",
                observation_location="Beijing"
            )

            # Can also override other parameters
            template = TemplateFactory.create(
                config,
                llm,
                embedder,
                language="zh",
                chunk_size=4096,
                max_workers=20
            )
        """
        config_mono = localize_template(config, language)

        if kwargs:
            base_options = config_mono.options or Options()
            options_dict = base_options.model_dump()
            options_dict.update(kwargs)
            config_mono.options = Options(**options_dict)

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

        creator = autotype_map.get(config_mono.type)
        if creator is None:
            raise ValueError(f"Unsupported type: {config_mono.type}")

        template = creator(config_mono, llm_client, embedder)
        display_extractors = cls.resolve_display_extractors(config_mono, {})

        return TemplateWrapper(template, display_extractors, config_mono.type)


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

        self._entity_label_extractor = display_extractors.get("entity_label_extractor")
        self._relation_label_extractor = display_extractors.get(
            "relation_label_extractor"
        )
        self._label_extractor = display_extractors.get("label_extractor")

    def __getattr__(self, name):
        return getattr(self._template, name)

    def show(self, **kwargs):
        """Automatically pass label_extractor parameters."""
        if self._autotype in (
            "graph",
            "hypergraph",
            "temporal_graph",
            "spatial_graph",
            "spatio_temporal_graph",
        ):
            if self._entity_label_extractor and self._relation_label_extractor:
                kwargs.setdefault(
                    "entity_label_extractor", self._entity_label_extractor
                )
                kwargs.setdefault(
                    "relation_label_extractor", self._relation_label_extractor
                )
        else:
            if self._label_extractor:
                kwargs.setdefault("label_extractor", self._label_extractor)

        return self._template.show(**kwargs)

    def search(self, **kwargs):
        return self._template.search(**kwargs)

    def chat(self, **kwargs):
        return self._template.chat(**kwargs)
