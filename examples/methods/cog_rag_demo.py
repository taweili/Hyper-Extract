"""
Cog_RAG Demo: Theme-based Knowledge Extraction + Entity-Relation Detail Retrieval

This demo demonstrates the unified Cog_RAG System Wrapper:
1. **Macro Layer (Theme Layer)**: Extracts Narrative Arcs (Themes) and their Participant Entities.
2. **Micro Layer (Detail Layer)**: Extracts Entities and their Semantic Relationships.
3. **Process**:
    - Feeds the same story to the Unified System.
    - The system automatically distributes extraction tasks to both layers.
    - Performs a Dual-Layer Chat/Search.

Usage:
    python examples/methods/cog_rag_demo.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.methods.rag import Cog_RAG

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing Cog-RAG System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        story = f.read()
    print(f"✅ Loaded {len(story)} characters")

    llm_client = ChatOpenAI(
        model="gpt-4o-mini",
    )
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    rag = Cog_RAG(
        llm_client=llm_client,
        embedder=embedder,
        chunk_size=1000,
    )

    print("\nFeeding story to the system...")
    rag.feed_text(story)
    print("✓ Story processed successfully\n")

    print("=" * 80)
    print("EXTRACTED THEMES (Macro Layer)")
    print("=" * 80)

    for i, theme in enumerate(rag.themes, 1):
        print(f"\n{i}. Theme: {theme.title}")
        print(f"   Summary: {theme.summary}")
        print(f"   Participants: {', '.join(theme.participants) if theme.participants else 'N/A'}")

    print(f"\n✓ Total themes extracted: {len(rag.themes)}\n")

    print("=" * 80)
    print("EXTRACTED ENTITIES (Micro Layer)")
    print("=" * 80)

    for node in rag.nodes:
        print(f"\n【{node.name}】(Type: {node.type})")
        print(f"  Description: {node.description}")

    print(f"\n✓ Total entities extracted: {len(rag.nodes)}\n")

    print("=" * 80)
    print("EXTRACTED RELATIONS (Micro Layer)")
    print("=" * 80)

    for i, edge in enumerate(rag.edges, 1):
        print(f"\n{i}. {edge.source} -> {edge.target}")
        print(f"   Description: {edge.description}")
        print(f"   Strength: {edge.strength}/10")

    print(f"\n✓ Total edges extracted: {len(rag.edges)}\n")

    print("=" * 80)
    print("Building Semantic Index...")
    print("=" * 80)

    rag.build_index()
    print("✓ Semantic index built successfully\n")

    print("=" * 80)
    print("Q&A: DUAL-LAYER SEARCH")
    print("=" * 80)

    queries = [
        "What happened to the crystal?",
        "What is the conspiracy?",
        "Who participated in the secret meeting?",
        "What is Leona's current situation?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n【Query {i}】{query}")
        print("-" * 60)

        try:
            themes, nodes, edges = rag.search(query, top_k=3)

            if themes:
                print("  Relevant Themes:")
                for t in themes[:2]:
                    print(f"    - {t.title}: {t.summary[:50]}...")

            if edges:
                print("  Relevant Relations:")
                for e in edges[:2]:
                    print(f"    - {e.source} -> {e.target}: {e.description[:50]}...")

        except Exception as e:
            print(f"  Search error: {str(e)}")

    print("\n" + "=" * 80)
    print("💬 Interactive Chat with Cog-RAG")
    print("=" * 80)
    print("Engaging in multi-turn dialogue based on extracted knowledge...\n")

    for q in queries:
        print(f"❓ User: {q}")
        try:
            response = rag.chat(q)
            print(f"🤖 Cog-RAG: {response.content}\n")
        except Exception as e:
            print(f"⚠️ Chat error: {e}\n")

    print("\n" + "=" * 80 + "\n")
