"""
iText2KG Demo: High-Quality Knowledge Graph Extraction

This demo shows how to use iText2KG to extract structured knowledge triples from unstructured text.
iText2KG uses a two-stage extraction strategy and enforces strict semantic Schema.

Usage:
    python examples/methods/itext2kg_demo.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.methods.typical import iText2KG

load_dotenv()

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing iText2KG System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"✅ Loaded {len(content)} characters")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    extractor = iText2KG(
        llm_client=llm,
        embedder=embedder,
    )

    print("\nExtracting knowledge from text...")
    extractor.feed_text(content)
    print("✓ Extraction completed\n")

    print("=" * 80)
    print("EXTRACTED ENTITIES")
    print("=" * 80)

    for i, node in enumerate(extractor.nodes, 1):
        print(f"\n{i}. {node.name} (Type: {node.type})")
        print(f"   Description: {node.description}")

    print(f"\n✓ Total entities: {len(extractor.nodes)}\n")

    print("=" * 80)
    print("EXTRACTED RELATIONS")
    print("=" * 80)

    for i, edge in enumerate(extractor.edges, 1):
        print(f"\n{i}. {edge.subject} -[{edge.predicate}]-> {edge.object}")
        print(f"   Confidence: {edge.confidence}")

    print(f"\n✓ Total relations: {len(extractor.edges)}\n")

    print("=" * 80)
    print("Building Index...")
    print("=" * 80)

    extractor.build_index()
    print("✓ Index built\n")

    print("=" * 80)
    print("Q&A: KNOWLEDGE SEARCH")
    print("=" * 80)

    queries = [
        "Who are the key characters?",
        "What is the main conflict?",
        "What events happened?",
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            nodes, edges = extractor.search(query, top_k=3)
            print("  Relevant entities:")
            for n in nodes[:3]:
                print(f"    - {n.name}")
            print("  Relevant relations:")
            for e in edges[:3]:
                print(f"    - {e.subject} {e.predicate} {e.object}")
        except Exception as e:
            print(f"  Error: {str(e)}")

    print("\n" + "=" * 80 + "\n")
