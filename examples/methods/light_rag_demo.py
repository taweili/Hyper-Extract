"""
Light-RAG Demo: Entity-Relationship Extraction with Standard Binary Graphs

This demo demonstrates:
1. Extracting entities and binary relationships from a complex sci-fi story.
2. Analysis of standard graph relationships (Source -> Target).
3. Semantic Search over the constructed Knowledge Graph (Q&A).

Usage:
    python examples/methods/light_rag_demo.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.methods.rag import Light_RAG

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing Light-RAG System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        story = f.read()
    print(f"✅ Loaded {len(story)} characters")

    llm_client = ChatOpenAI(
        model="gpt-4o-mini",
    )
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    rag = Light_RAG(
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
    print("EXTRACTED EDGES (Binary Relationships)")
    print("=" * 80)

    for i, edge in enumerate(rag.edges, 1):
        print(f"\n{i}. {edge.source} -> {edge.target}")
        print(f"   Description: {edge.description}")
        print(f"   Keywords: {edge.keywords}")
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

    print("\nEntity Centrality (Degree):")
    centrality = {}
    for edge in rag.edges:
        centrality[edge.source] = centrality.get(edge.source, 0) + 1
        centrality[edge.target] = centrality.get(edge.target, 0) + 1

    for entity, count in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {entity}: {count}")

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
        "What is the conspiracy between the characters?",
        "Who participated in the secret meeting?",
        "What is Leona's current situation?",
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
                    print(f"     Relation: {edge.source} -> {edge.target}")
                    print(f"     Description: {edge.description}")
                    print(f"     Strength: {edge.strength}/10")
            else:
                print("  (No relevant relationships found)")
        except Exception as e:
            print(f"  Search error: {str(e)}")

    print("\n" + "=" * 80)
    print("💬 Interactive Chat with LightRAG")
    print("=" * 80)
    print("Engaging in multi-turn dialogue based on extracted knowledge...\n")

    for q in queries:
        print(f"❓ User: {q}")
        try:
            response = rag.chat(q)
            print(f"🤖 LightRAG: {response.content}\n")
        except Exception as e:
            print(f"⚠️ Chat error: {e}\n")

    print("\n" + "=" * 80)
    print("Saving Results...")
    print("=" * 80)

    try:
        output_dir = "temp/light_rag_demo"
        rag.dump(output_dir)
        print(f"✓ Results saved to {output_dir}/")

        saved_files = []
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                    saved_files.append(rel_path)

        if saved_files:
            print("\n  Saved files:")
            for f in saved_files:
                print(f"    - {f}")
    except Exception as e:
        print(f"⚠️ Warning: Could not save results: {str(e)}")

    print("\n" + "=" * 80 + "\n")
