"""
Graph RAG Demo: Tesla Biography Knowledge Graph

Extract and query knowledge from Tesla's biography using Graph RAG.

Usage:
    python examples/en/methods/graph_rag_demo.py
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.methods.rag import Graph_RAG

load_dotenv()

INPUT_FILE = project_root / "examples" / "en" / "tesla.md"
QUESTION_FILE = project_root / "examples" / "en" / "tesla_question.md"

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        text = f.read()
    with open(QUESTION_FILE) as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini")
    embedder = OpenAIEmbeddings()

    print("=" * 60)
    print("Graph RAG Demo")
    print("=" * 60)

    rag = Graph_RAG(llm_client=llm, embedder=embedder)
    rag.feed_text(text)

    print(f"\n✓ Extracted {len(rag.nodes)} entities, {len(rag.edges)} relations\n")

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = rag.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")
