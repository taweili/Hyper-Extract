"""
AutoModel Demo - Tesla Biography Summary

Extract a structured summary from text using AutoModel.
This demo shows how to merge multiple chunks into one consistent object.

Usage:
    python examples/en/autotypes/model_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from typing import List, Optional
from hyperextract import AutoModel


class BiographySummary(BaseModel):
    """Biography summary schema"""
    title: str = Field(description="Title of the biography")
    subject: str = Field(description="Main subject name")
    birth_year: Optional[str] = Field(default="", description="Year of birth")
    death_year: Optional[str] = Field(default="", description="Year of death")
    nationality: str = Field(description="Nationality", default="")
    occupation: List[str] = Field(default_factory=list, description="Main occupations")
    summary: str = Field(description="Brief summary")
    major_inventions: List[str] = Field(default_factory=list, description="Major inventions")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  AutoModel Demo - Tesla Summary")
    print("=" * 60)
    print("Extracting biography summary...")

    model = AutoModel(
        data_schema=BiographySummary,
        llm_client=llm,
        embedder=embedder,
    )

    model.feed_text(text)

    data = model.data
    print(f"\nSubject: {data.subject}")
    print(f"Lifespan: {data.birth_year} - {data.death_year}")
    print(f"Nationality: {data.nationality}")
    print(f"\nSummary: {data.summary}")

    if data.major_inventions:
        print(f"\nMajor Inventions:")
        for inv in data.major_inventions[:3]:
            print(f"  - {inv}")

    model.build_index()

    for q in ["inventions", "Edison", "legacy"]:
        print(f"\nQuery: {q}")
        results = model.search(q, top_k=2)
        for r in results:
            print(f"  {r}")


if __name__ == "__main__":
    main()
