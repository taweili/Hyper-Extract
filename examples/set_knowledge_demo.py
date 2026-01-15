"""Set Knowledge Demo - Extracting unique skills from multiple job descriptions

This example demonstrates how SetKnowledge automatically deduplicates
extracted items based on a unique key field.
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.knowledge.generic.set import SetKnowledge
from hyperextract.utils.merger import MergeStrategy


# Define the schema for skills
class SkillSchema(BaseModel):
    """A skill mentioned in job descriptions"""

    name: str = Field(
        description="Name of the skill (e.g., 'Python', 'Machine Learning')"
    )
    category: str | None = Field(
        None,
        description="Category (e.g., 'Programming Language', 'Framework', 'Soft Skill')",
    )
    proficiency_level: str | None = Field(
        None,
        description="Required proficiency level if mentioned (e.g., 'Expert', 'Intermediate')",
    )
    description: str | None = Field(
        None, description="Brief description or context of how the skill is used"
    )


def main():
    # Initialize LLM and embeddings
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(base_url=os.getenv("OPENAI_BASE_URL"))

    # Create SetKnowledge with FIELD_MERGE strategy
    # This means when the same skill appears multiple times,
    # the new extraction will fill in any missing fields from the existing one
    skills = SetKnowledge(
        item_schema=SkillSchema,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,  # Deduplicate based on skill name
        merge_item_strategy=MergeStrategy.FIELD_MERGE,
        prompt="""Extract all technical skills, frameworks, tools, and soft skills mentioned in the text.
        
For each skill, provide:
- name: The exact name of the skill
- category: What type of skill it is
- proficiency_level: If mentioned, the required level
- description: Brief context about how it's used

Be specific and extract all mentioned skills.""",
    )

    # Sample job descriptions (with overlapping skills)
    job_descriptions = [
        """
        Senior Python Developer
        
        We are seeking an expert Python developer with 5+ years of experience.
        
        Requirements:
        - Expert level Python programming
        - Strong experience with FastAPI framework for building REST APIs
        - Proficiency in PostgreSQL database design and optimization
        - Experience with Docker for containerization
        - Strong problem-solving and communication skills
        - Experience with Git version control
        """,
        """
        Full Stack Engineer
        
        Join our dynamic team as a Full Stack Engineer!
        
        Required Skills:
        - Python for backend development (3+ years)
        - React for frontend development
        - Experience with FastAPI or Django
        - PostgreSQL or MySQL database experience
        - Docker and Kubernetes for deployment
        - Excellent teamwork and communication abilities
        - Git workflow knowledge
        """,
        """
        Machine Learning Engineer
        
        Looking for an ML Engineer to join our AI team.
        
        Must Have:
        - Advanced Python skills for ML development
        - PyTorch or TensorFlow experience
        - Strong understanding of machine learning algorithms
        - Experience with Docker for model deployment
        - PostgreSQL for data storage
        - Git for code versioning
        - Strong analytical and problem-solving skills
        """,
    ]

    print("=" * 80)
    print("SET KNOWLEDGE DEMO: Extracting Unique Skills from Job Descriptions")
    print("=" * 80)

    # Extract skills from all job descriptions
    print("\n📄 Processing job descriptions...")
    for i, job_desc in enumerate(job_descriptions, 1):
        print(f"\n  Processing job description {i}...")
        skills.extract(job_desc)
        print(f"  ✓ Total unique skills so far: {len(skills)}")

    # Display all unique skills
    print("\n" + "=" * 80)
    print(f"📊 EXTRACTED UNIQUE SKILLS: {len(skills)} total")
    print("=" * 80)

    # Group by category
    skills_by_category = {}
    for skill in skills.items:
        category = skill.category or "Uncategorized"
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)

    # Display organized results
    for category, category_skills in sorted(skills_by_category.items()):
        print(f"\n{category}:")
        for skill in sorted(category_skills, key=lambda s: s.name):
            print(f"  • {skill.name}")
            if skill.proficiency_level:
                print(f"    Level: {skill.proficiency_level}")
            if skill.description:
                print(f"    Context: {skill.description}")

    # Demonstrate set operations
    print("\n" + "=" * 80)
    print("🔍 DEMONSTRATING SET OPERATIONS")
    print("=" * 80)

    # Build index for semantic search
    print("\nBuilding vector index for semantic search...")
    skills.build_index()
    print("✓ Index built successfully")

    # Search for related skills
    print("\n1. Semantic Search - Finding skills related to 'backend development':")
    backend_skills = skills.search("backend development", top_k=5)
    for skill in backend_skills:
        print(f"  • {skill.name}")
        if skill.category:
            print(f"    Category: {skill.category}")

    # Check if specific skills exist
    print("\n2. Membership Testing:")
    test_skills = ["Python", "Java", "Docker", "Rust"]
    for skill_name in test_skills:
        exists = skills.contains(skill_name)
        status = "✓" if exists else "✗"
        print(f"  {status} {skill_name}: {'Found' if exists else 'Not found'}")

    # Get specific skill details
    print("\n3. Get Specific Skill Details:")
    python_skill = skills.get("Python")
    if python_skill:
        print(f"  Skill: {python_skill.name}")
        print(f"  Category: {python_skill.category}")
        print(f"  Level: {python_skill.proficiency_level or 'Not specified'}")
        print(f"  Description: {python_skill.description or 'No description'}")

    # Save the extracted knowledge
    print("\n" + "=" * 80)
    print("💾 SAVING EXTRACTED KNOWLEDGE")
    print("=" * 80)

    save_path = "tmp/set_knowledge_demo"
    skills.dump(save_path)
    print(f"✓ Saved to: {save_path}")
    print("  - state.json (structured data)")
    print("  - faiss_index/ (vector index for semantic search)")

    # Demonstrate loading
    print("\n📂 Loading saved knowledge...")
    loaded_skills = SetKnowledge(
        item_schema=SkillSchema,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,
    )
    loaded_skills.load(save_path)
    print(f"✓ Loaded {len(loaded_skills)} unique skills")

    # Summary
    print("\n" + "=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    print(f"  Total unique skills extracted: {len(skills)}")
    print(f"  Job descriptions processed: {len(job_descriptions)}")
    print("  Deduplication strategy: FIELD_MERGE")
    print("  Key extractor: lambda x: x.name")
    print("\n  ✓ Automatically deduplicated based on skill names")
    print("  ✓ Merged information from multiple occurrences")
    print("  ✓ Supports semantic search across all skills")
    print("  ✓ Persistent storage with dump/load")
    print("=" * 80)


if __name__ == "__main__":
    main()
