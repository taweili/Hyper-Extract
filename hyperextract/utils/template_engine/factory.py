"""Template Factory - Dynamically creates template instances from configuration.

Supports all 8 AutoType dynamic generation.
"""

from typing import TYPE_CHECKING

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

        entity_schema, relation_schema = parse_output(config.output)
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
        template = localize_template(config, language)

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

        creator = autotype_map.get(template.type)
        template = creator(template, llm_client, embedder, **kwargs)
        return template

    @classmethod
    def create_from_name(
        cls,
        name: str,
        lang: str = "zh",
        llm_client=None,
        embedder=None,
        **kwargs,
    ):
        """Create template instance by template name.

        Args:
            name: Template name (e.g., "knowledge_graph", "zh/finance/risk_assessment")
            lang: Language, default "zh"
            llm_client: LLM client, optional, reads from global config if not provided
            embedder: Embedder client, optional, reads from global config if not provided
            **kwargs: Additional parameters (e.g., observation_time, observation_location)

        Returns:
            AutoType instance

        Examples:
            # Use global config (recommended)
            template = TemplateFactory.create_from_name("knowledge_graph")

            # Custom client
            template = TemplateFactory.create_from_name("knowledge_graph", llm_client=llm, embedder=emb)

            # With additional parameters
            template = TemplateFactory.create_from_name("FinancialTemporalGraph", observation_time="2024-06-15")
        """
        from .gallery import Gallery

        config = Gallery.get(name)
        if config is None:
            config = Gallery.get(f"{lang}/{name}")

        if config is None:
            available = Gallery.list_all()
            raise ValueError(
                f"Template '{name}' not found. Available: {available[:10]}..."
            )

        if llm_client is None or embedder is None:
            from hyperextract.utils import get_client

            default_llm, default_emb = get_client()
            llm_client = llm_client or default_llm
            embedder = embedder or default_emb

        return cls.create(config, llm_client, embedder, language=lang, **kwargs)
