"""
Atom Demo: Temporal Knowledge Graph Extraction from Product History

This demo demonstrates how to use Atom to extract structured knowledge from product iteration history.
Key features:
1. Extracting product release dates and version information
2. Key person and product associations
3. Company acquisitions and product strategy changes
4. Precise capture of temporal relationships (t_start, t_end)
5. Evidence tracking and source tracing

Usage:
    python examples/methods/atom_demo.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.methods.typical import Atom

load_dotenv()

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing Atom System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"✅ Loaded {len(content)} characters")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    atom = Atom(
        llm_client=llm,
        embedder=embedder,
        observation_time="3042-12-01",
    )

    print("\nFeeding content to the system...")
    atom.feed_text(content)
    print("✓ Content processed successfully\n")

    print("=" * 80)
    print("EXTRACTED FACTS")
    print("=" * 80)

    for i, fact in enumerate(atom.facts, 1):
        print(f"\n{i}. Subject: {fact.subject}")
        print(f"   Predicate: {fact.predicate}")
        print(f"   Object: {fact.object}")
        print(f"   Start Time: {fact.t_start}")
        print(f"   End Time: {fact.t_end}")
        print(f"   Source: {fact.source}")

    print(f"\n✓ Total facts extracted: {len(atom.facts)}\n")

    print("=" * 80)
    print("TEMPORAL STATISTICS")
    print("=" * 80)

    print(f"\nEarliest event: {min(f.t_start for f in atom.facts if f.t_start)}")
    print(f"Latest event: {max(f.t_end for f in atom.facts if f.t_end)}")

    print("\n" + "=" * 80)
    print("Q&A: TEMPORAL SEARCH")
    print("=" * 80)

    queries = [
        "What events occurred?",
        "Who are the key participants?",
        "What is the timeline of events?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n【Query {i}】{query}")
        print("-" * 60)

        try:
            facts = atom.search(query, top_k=5)
            for fact in facts:
                print(f"  - {fact.subject} {fact.predicate} {fact.object}")
                if fact.t_start:
                    print(f"    Time: {fact.t_start}")
        except Exception as e:
            print(f"  Search error: {str(e)}")

    print("\n" + "=" * 80 + "\n")
