# Hyper-Extract Template Development & Master Prompt Protocol

This document defines the standard workflow for implementing domain-specific knowledge extraction templates in the `Hyper-Extract` framework.

## 0. Core Protocol: Source-First

Before writing any code, you MUST:
1.  **Identify the Base Class**: Choose the appropriate base class from the mapping table below.
2.  **Read the Source**: Use tools to read the Python source code of the chosen base class (located in `hyperextract/types/`).
    *   *Reason*: Source code is the source of truth for `__init__` parameters, `show` method signatures, and generic constraints.

## 1. Design Phase: Feasibility & Selection

### The Extractability Rule
Before designing a Schema, ask yourself:
*   **Evidence Availability**: Does the input text explicitly contain evidence for this field? (Do not design fields for dynamic data typically found in external databases).
*   **Structural Fit**: What is the most natural form for this data? (e.g., Unordered repeating patterns, unique set, or complex N-ary relations?)

### Mapping Table for Base Class Selection

| Data Nature | Recommended Base Class | Source Code Location | Key Constraints |
| :--- | :--- | :--- | :--- |
| **Single Object** (Summary/Meta) | `AutoModel` | `hyperextract/types/model.py` | One object per document |
| **Pattern Collection** (Repeating) | `AutoList` | `hyperextract/types/list.py` | No deduplication. Extracts all instances found. |
| **Unique Collection** (Glossary) | `AutoSet` | `hyperextract/types/set.py` | Auto-deduplication; requires `key_extractor` |
| **Binary Graph** (Entity-Relation) | `AutoGraph` | `hyperextract/types/graph.py` | Standard binary relationships |
| **Temporal Graph** (Timestamps) | `AutoTemporalGraph` | `hyperextract/types/temporal_graph.py` | Edges MUST have time fields |
| **Spatial Graph** (Locations) | `AutoSpatialGraph` | `hyperextract/types/spatial_graph.py` | Nodes/Edges MUST have location/coords |
| **Spatio-Temporal Graph** | `AutoSpatioTemporalGraph` | `hyperextract/types/spatio_temporal_graph.py` | Tracks movement and evolution in space/time |
| **N-ary/Complex Events** | `AutoHypergraph` | `hyperextract/types/hypergraph.py` | Hyperedge connects N nodes |

---

## 2. Implementation Rules

### A. Prompt Definition
*   **Mandatory Constant**: Define `_TEMPLATE_PROMPT` (a multi-line string) outside the class.
*   **Content**: Clearly define the expert persona and extraction logic. Mention specific formatting rules if necessary.

### B. Class Structure
*   **Schemas**: All Pydantic fields MUST include a `description` attribute. This is vital for the LLM to understand the target.
*   **Initialization**: Explicitly list parameters (`llm_client`, `embedder`, etc.) and pass the prompt to `super().__init__(..., prompt=_TEMPLATE_PROMPT, ...)`.
*   **Visualization (`show`)**: YOU MUST override the `show` method.
    *   **Parameter Constraint**: **DO NOT** include `label_extractor` parameters (e.g., `node_label_extractor`) in the template's `show` method signature.
    *   **Implementation**: You should define the best **frontend visualization labels** and their extraction logic for your specific Schema internally within `show` and pass them to `super().show(...)`. This ensures users get the best visualization out-of-the-box by simply calling `template.show()`.

---

## 3. Standard Skeleton

```python
from typing import Any, Callable
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import ... # Import relevant base class

# 1. Define Schemas
class ItemSchema(BaseModel):
    name: str = Field(..., description="Name of the entity")
    ...

# 2. Define Prompt
_TEMPLATE_PROMPT = """
You are an expert in [Domain]. Your task is to extract [Structure] from text...
"""

# 3. Define Class
class MyTemplate(AutoType[ItemSchema]): # Replace with actual base class (AutoList, AutoSet, etc.)
    """Google Style Docstring."""

    def __init__(
        self, 
        llm_client: BaseChatModel, 
        embedder: Embeddings, 
        chunk_size: int = 2048,
        **kwargs: Any
    ):
        super().__init__(
            item_schema=ItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_TEMPLATE_PROMPT,
            chunk_size=chunk_size,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ): 
        # Define frontend visualization labels internally
        def my_label_extractor(item: ItemSchema) -> str:
            return item.name

        super().show(
            item_label_extractor=my_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
```
