from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class IngredientState(BaseModel):
    """
    The state of ingredients/materials at a particular stage in the recipe process.
    """

    name: str = Field(
        description="State descriptor (e.g., 'Blended Mixture', 'Heated Dough', 'Cooled Slurry')."
    )
    composition: str = Field(
        description="What's in this state (e.g., 'Eggs + Sugar', 'Flour + Water + Salt')."
    )
    physical_state: Optional[str] = Field(
        None, description="Physical form: 'Liquid', 'Solid', 'Powder', 'Dough', 'Emulsion', 'Foam'."
    )


class ProcessingStep(BaseModel):
    """
    A transformation step connecting two ingredient states.
    """

    step_id: str = Field(description="Step identifier (e.g., 'Step 1', '1.1', 'Mixing').")
    source_state: str = Field(description="The starting ingredient state.")
    target_state: str = Field(description="The resulting ingredient state after processing.")
    action: str = Field(
        description="The processing action (e.g., 'Blend', 'Heat', 'Cool', 'Rest', 'Knead', 'Ferment')."
    )
    process_conditions: Optional[str] = Field(
        None, description="Combine duration, temp, equipment, and parameters."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a food scientist. Extract recipe process steps.\n\n"
    "Rules:\n"
    "- Identify processing actions and transformations.\n"
    "- Extract ingredient states pre/post step.\n"
    "- Capture **process_conditions** (time, temp, equipment).\n"
    "- Maintain sequence order."
)

_NODE_PROMPT = (
    "You are a food scientist. Extract ingredient states (Nodes).\n\n"
    "Rules:\n"
    "- Identify distinct states (raw, mixed, cooked).\n"
    "- List ingredients present.\n"
    "- Note physical form."
)

_EDGE_PROMPT = (
    "You are a food scientist. Extract processing steps (Edges).\n\n"
    "Rules:\n"
    "- Connect source to target state via action.\n"
    "- **process_conditions**: Time, temperature, equipment.\n"
    "- Maintain exact step order.\n"
    "- Only connect existing nodes."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class RecipeProcessGraph(AutoTemporalGraph[IngredientState, ProcessingStep]):
    """
    Applicable to: Industrial Formulation Sheets, Recipe SOPs, Food Science Research,
    Production Batch Records, Chef's Recipes, Cooking Manuals, R&D Experimental Protocols.

    Template for extracting and mapping sequential food production processes with 
    precise timing and parameters. Enables recipe standardization, process optimization, 
    and knowledge transfer in culinary and industrial food settings.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> recipe = RecipeProcessGraph(llm_client=llm, embedder=embedder)
        >>> process = "Step 1: Blend eggs and sugar for 5 mins. Step 2: Heat to 175°C..."
        >>> recipe.feed_text(process)
        >>> recipe.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Recipe Process Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for state and step extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=IngredientState,
            edge_schema=ProcessingStep,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.step_id.strip(),
            nodes_in_edge_extractor=lambda x: (
                x.source_state.strip(),
                x.target_state.strip(),
            ),
            time_in_edge_extractor=lambda x: x.step_id.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        Visualize the recipe process timeline using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of states to retrieve. Default 3.
            top_k_edges_for_search (int): Number of steps to retrieve. Default 3.
            top_k_nodes_for_chat (int): States for chat context. Default 3.
            top_k_edges_for_chat (int): Steps for chat context. Default 3.
        """

        def node_label_extractor(node: IngredientState) -> str:
            return f"{node.name} ({node.physical_state if node.physical_state else 'Unknown'})"

        def edge_label_extractor(edge: ProcessingStep) -> str:
            temp = f" ({edge.process_conditions})" if edge.process_conditions else ""
            return f"{edge.action}{temp}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
