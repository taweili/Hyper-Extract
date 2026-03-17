"""Template Factory - Dynamically creates template instances from configuration.

Supports all 8 AutoType dynamic generation.
"""

from typing import TYPE_CHECKING, Union
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .parsers import (
    TemplateCfg,
    localize_template,
    parse_output,
    parse_identifiers,
    parse_guideline,
    parse_option,
    parse_display,
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
    @classmethod
    def create_model(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoModel":
        """Create AutoModel template."""
        from hyperextract.types import AutoModel

        data_schema = parse_output(config.output, config.type)
        prompt = parse_guideline(config.guideline, config.type)
        options = parse_option(config.options, config.type, override=kwargs)
        label_extractor = parse_display(config.display, config.type)

        return AutoModel(
            data_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            label_extractor=label_extractor,
            **options,
        )

    @classmethod
    def create_list(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoList":
        """Create AutoList template."""
        from hyperextract.types import AutoList

        data_schema = parse_output(config.output, config.type)
        prompt = parse_guideline(config.guideline, config.type)
        options = parse_option(config.options, config.type, override=kwargs)
        item_label_extractor = parse_display(config.display, config.type)

        return AutoList(
            item_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            item_label_extractor=item_label_extractor,
            **options,
        )

    @classmethod
    def create_set(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoSet":
        """Create AutoSet template."""
        from hyperextract.types import AutoSet

        data_schema = parse_output(config.output, config.type)
        item_id_extractor = parse_identifiers(config.identifiers, config.type)
        prompt = parse_guideline(config.guideline, config.type)
        options = parse_option(config.options, config.type, override=kwargs)
        item_label_extractor = parse_display(config.display, config.type)

        return AutoSet(
            item_schema=data_schema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=item_id_extractor,
            item_label_extractor=item_label_extractor,
            prompt=prompt,
            **options,
        )

    @classmethod
    def create_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoGraph":
        """Create AutoGraph template."""
        from hyperextract.types import AutoGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        entity_key_extractor, relation_key_extractor, entities_in_relation_extractor = (
            identifiers
        )
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_hypergraph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoHypergraph":
        """Create AutoHypergraph template."""
        from hyperextract.types import AutoHypergraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        entity_key_extractor, relation_key_extractor, entities_in_relation_extractor = (
            identifiers
        )
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoHypergraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_temporal_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoTemporalGraph":
        from hyperextract.types import AutoTemporalGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        (
            entity_key_extractor,
            relation_key_extractor,
            entities_in_relation_extractor,
            time_in_edge_extractor,
        ) = parse_identifiers(config.identifiers, config.type)

        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoTemporalGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            llm_client=llm_client,
            embedder=embedder,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            time_in_edge_extractor=time_in_edge_extractor,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_spatial_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoSpatialGraph":
        """Create AutoSpatialGraph template."""
        from hyperextract.types import AutoSpatialGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        (
            entity_key_extractor,
            relation_key_extractor,
            entities_in_relation_extractor,
            location_in_edge_extractor,
        ) = identifiers
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoSpatialGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            location_in_edge_extractor=location_in_edge_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create_spatio_temporal_graph(
        cls,
        config: TemplateCfg,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ) -> "AutoSpatioTemporalGraph":
        """Create AutoSpatioTemporalGraph template."""
        from hyperextract.types import AutoSpatioTemporalGraph

        entity_schema, relation_schema = parse_output(config.output, config.type)
        identifiers = parse_identifiers(config.identifiers, config.type)
        (
            entity_key_extractor,
            relation_key_extractor,
            entities_in_relation_extractor,
            time_in_edge_extractor,
            location_in_edge_extractor,
        ) = identifiers
        prompt, prompt_for_entity_extraction, prompt_for_relation_extraction = (
            parse_guideline(config.guideline, config.type)
        )
        node_label_extractor, edge_label_extractor = parse_display(
            config.display, config.type
        )
        options = parse_option(config.options, config.type, override=kwargs)

        return AutoSpatioTemporalGraph(
            node_schema=entity_schema,
            edge_schema=relation_schema,
            node_key_extractor=entity_key_extractor,
            edge_key_extractor=relation_key_extractor,
            nodes_in_edge_extractor=entities_in_relation_extractor,
            time_in_edge_extractor=time_in_edge_extractor,
            location_in_edge_extractor=location_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt,
            prompt_for_node_extraction=prompt_for_entity_extraction,
            prompt_for_edge_extraction=prompt_for_relation_extraction,
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            **options,
        )

    @classmethod
    def create(
        cls,
        source: Union[str, Path, TemplateCfg],
        language: str,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs,
    ):
        """Create template instance based on configuration.

        Args:
            source: Template source - can be:
                - str: Template name (e.g., "knowledge_graph") or file path
                - Path: YAML file path
                - TemplateCfg: Template configuration instance
            language: Language code for localization (e.g., 'zh', 'en') - required
            llm_client: LLM client
            embedder: Embedding model
            **kwargs: Additional parameters to override config parameters
                e.g., observation_time="2024-06-15", observation_location="Beijing"

        Returns:
            AutoType instance

        Examples:
            # By name (search via Gallery)
            template = TemplateFactory.create("knowledge_graph", "zh", llm, embedder)

            # By file path
            template = TemplateFactory.create("/path/to/template.yaml", "zh", llm, embedder)

            # By TemplateCfg instance
            template = TemplateFactory.create(config, "zh", llm, embedder)

            # For specific language
            template = TemplateFactory.create("knowledge_graph", "en", llm, embedder)

            # For spatio-temporal templates, pass observation_time etc.
            template = TemplateFactory.create(
                "FinancialTemporalGraph",
                "zh",
                llm,
                embedder,
                observation_time="2024-06-15",
                observation_location="Beijing"
            )

            # Can also override other parameters
            template = TemplateFactory.create(
                "knowledge_graph",
                llm,
                embedder,
                language="zh",
                chunk_size=4096,
                max_workers=20
            )
        """
        from .gallery import Gallery
        from .parsers import load_template

        match source:
            case str() as s if s.endswith(".yaml") or Path(s).exists():
                config = load_template(s)
            case str() as s:
                config = Gallery.get(s)
            case Path() as p if p.exists():
                config = load_template(p)
            case _:
                raise ValueError("Invalid source: must be a template path or file path")

        if config is None:
            raise ValueError(f"Template not found: {source}")

        template = localize_template(config, language)

        match template.type:
            case "model":
                template = cls.create_model(template, llm_client, embedder, **kwargs)
            case "list":
                template = cls.create_list(template, llm_client, embedder, **kwargs)
            case "set":
                template = cls.create_set(template, llm_client, embedder, **kwargs)
            case "graph":
                template = cls.create_graph(template, llm_client, embedder, **kwargs)
            case "hypergraph":
                template = cls.create_hypergraph(
                    template, llm_client, embedder, **kwargs
                )
            case "temporal_graph":
                template = cls.create_temporal_graph(
                    template, llm_client, embedder, **kwargs
                )
            case "spatial_graph":
                template = cls.create_spatial_graph(
                    template, llm_client, embedder, **kwargs
                )
            case "spatio_temporal_graph":
                template = cls.create_spatio_temporal_graph(
                    template, llm_client, embedder, **kwargs
                )
        return template
