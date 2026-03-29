"""
HyperGraph-RAG Demo: Extracting Hyperedges from Text

This script demonstrates the usage of the HyperGraph_RAG system, which is designed
to extract hyperedges from text.

Usage:
    python examples/methods/hypergraph_rag_demo.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.methods.rag import HyperGraph_RAG

load_dotenv()

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing HyperGraph-RAG System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        story = f.read()
    print(f"✅ Loaded {len(story)} characters")

    llm_client = ChatOpenAI(
        model="gpt-4o-mini",
    )
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    rag = HyperGraph_RAG(
        llm_client=llm_client,
        embedder=embedder,
        chunk_size=1000,
    )

    print("\nFeeding story to the system...")
    rag.feed_text(story)
    print("✓ Story processed successfully\n")

    print("=" * 80)
    print("EXTRACTED ENTITIES")
    print("=" * 80)

    for node in rag.nodes:
        print(f"\n【{node.name}】(Type: {node.type})")
        print(f"  Description: {node.description}")

    print(f"\n✓ Total entities extracted: {len(rag.nodes)}\n")

    print("=" * 80)
    print("EXTRACTED HYPEREDGES")
    print("=" * 80)

    for i, edge in enumerate(rag.edges, 1):
        print(f"\n{i}. Participants: {' <-> '.join(edge.participants)}")
        print(f"   Description: {edge.description}")
        keywords_str = ", ".join(edge.keywords) if edge.keywords else "N/A"
        print(f"   Keywords: {keywords_str}")
        print(f"   Strength: {edge.strength}/10")

    print(f"\n✓ Total edges extracted: {len(rag.edges)}\n")

    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)

    type_counts = {}
    for node in rag.nodes:
        type_counts[node.type] = type_counts.get(node.type, 0) + 1

    print("\nEntity Type Distribution:")
    for entity_type, count in sorted(type_counts.items()):
        print(f"  {entity_type}: {count}")

    if rag.edges:
        avg_strength = sum(e.strength for e in rag.edges) / len(rag.edges)
        print(f"\nAverage Edge Strength: {avg_strength:.2f}/10")

    print("\n" + "=" * 80)
    print("Building Semantic Index...")
    print("=" * 80)

    rag.build_index()
    print("✓ Semantic index built successfully\n")

    print("=" * 80)
    print("Q&A: SEMANTIC SEARCH")
    print("=" * 80)

    queries = [
        "What happened to the crystal?",
        "What is the conspiracy?",
        "Who participated in the secret meeting?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n【Query {i}】{query}")
        print("-" * 60)

        try:
            results = rag.search_edges(query, top_k=3)

            if results:
                for j, result in enumerate(results, 1):
                    edge = result[0] if isinstance(result, tuple) else result
                    score = result[1] if isinstance(result, tuple) else 1.0

                    print(f"\n  {j}. [Score: {score:.3f}]")
                    print(f"     Participants: {' <-> '.join(edge.participants)}")
                    print(f"     Description: {edge.description}")
            else:
                print("  (No relevant relationships found)")
        except Exception as e:
            print(f"  Search error: {str(e)}")

    print("\n" + "=" * 80 + "\n")
