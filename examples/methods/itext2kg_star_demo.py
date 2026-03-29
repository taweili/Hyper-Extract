"""
iText2KG_Star Demo: Knowledge Graph Extraction with Semantic Deduplication

This demo shows the advanced features of iText2KG_Star:
1. Single-stage extraction: Directly extract relations (triples) from text, automatically deriving entities.
2. Semantic deduplication: Use SemHash algorithm to merge similar entities.

Usage:
    python examples/methods/itext2kg_star_demo.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.methods.typical import iText2KG_Star

load_dotenv()

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing iText2KG_Star System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"✅ Loaded {len(content)} characters")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    extractor = iText2KG_Star(
        llm_client=llm,
        embedder=embedder,
    )

    print("\nExtracting knowledge with deduplication...")
    extractor.feed_text(content)
    print("✓ Extraction completed\n")

    print("=" * 80)
    print("EXTRACTED ENTITIES (After Deduplication)")
    print("=" * 80)

    for i, node in enumerate(extractor.nodes, 1):
        print(f"\n{i}. {node.name} (Type: {node.type})")
        print(f"   Description: {node.description}")

    print(f"\n✓ Total unique entities: {len(extractor.nodes)}\n")

    print("=" * 80)
    print("EXTRACTED RELATIONS")
    print("=" * 80)

    for i, edge in enumerate(extractor.edges, 1):
        print(f"\n{i}. {edge.subject} -[{edge.predicate}]-> {edge.object}")

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
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            nodes, edges = extractor.search(query, top_k=3)
            for n in nodes[:3]:
                print(f"  Entity: {n.name}")
            for e in edges[:3]:
                print(f"  Relation: {e.subject} {e.predicate} {e.object}")
        except Exception as e:
            print(f"  Error: {str(e)}")

    print("\n" + "=" * 80 + "\n")
