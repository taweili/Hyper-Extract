"""
UnitKnowledge 使用示例

演示如何使用 UnitKnowledge 类进行知识提取、搜索、保存和加载。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.knowledge.generic import UnitKnowledge


# 1. 定义知识 Schema
class ArticleKnowledge(BaseModel):
    """文章知识结构"""

    title: str = Field(default="", description="文章标题")
    author: str = Field(default="", description="作者")
    summary: str = Field(default="", description="摘要")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    topics: List[str] = Field(default_factory=list, description="主题标签")


def main():
    print("=" * 60)
    print("UnitKnowledge 使用示例")
    print("=" * 60)

    # 2. 初始化 LLM 和 Embedder
    print("\n[1] 初始化 LLM 和 Embedder...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. 创建 UnitKnowledge 实例
    print("[2] 创建 UnitKnowledge 实例...")
    knowledge = UnitKnowledge(
        data_schema=ArticleKnowledge,
        llm_client=llm,
        embedder=embedder,
        prompt="",  # 使用默认 prompt
        chunk_size=2000,
        max_workers=5,
        show_progress=True,
    )

    # 4. 提取知识
    print("\n[3] 从文本中提取知识...")
    sample_text = """
    Title: The Future of Artificial Intelligence
    Author: Dr. Jane Smith
    
    Artificial intelligence (AI) is rapidly transforming our world. This groundbreaking 
    technology has the potential to revolutionize industries ranging from healthcare to 
    transportation. In this article, we explore the key developments and future directions 
    of AI research.
    
    Key Points:
    1. Machine learning algorithms are becoming increasingly sophisticated
    2. AI is being applied to solve complex real-world problems
    3. Ethical considerations are crucial in AI development
    4. Collaboration between humans and AI will define the future
    
    Topics: artificial intelligence, machine learning, ethics, future technology
    """

    result = knowledge.extract(sample_text)
    print(f"✓ 提取完成: {result}")

    # 5. 查看提取的数据
    print("\n[4] 查看提取的知识数据:")
    extracted_data = knowledge.data
    print(f"  标题: {extracted_data.title}")
    print(f"  作者: {extracted_data.author}")
    print(f"  摘要: {extracted_data.summary[:100]}...")
    print(f"  关键要点数量: {len(extracted_data.key_points)}")
    print(f"  主题标签: {', '.join(extracted_data.topics)}")

    # 6. 构建索引
    print("\n[5] 构建向量索引...")
    knowledge.build_index()
    print(f"✓ 索引构建完成，共 {knowledge.size()} 个字段")

    # 7. 语义搜索
    print("\n[6] 执行语义搜索...")
    search_query = "What are the main topics of this article?"
    results = knowledge.search(search_query, top_k=3)
    print(f"  查询: {search_query}")
    print(f"  搜索结果数量: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"  结果 {i}: {result}")

    # 8. 保存知识
    print("\n[7] 保存知识到文件夹...")
    save_path = Path(__file__).parent.parent / "tmp" / "article_knowledge"
    knowledge.dump(save_path)
    print(f"✓ 知识已保存到: {save_path}")

    # 9. 加载知识
    print("\n[8] 从文件夹加载知识...")
    new_knowledge = UnitKnowledge(
        data_schema=ArticleKnowledge,
        llm_client=llm,
        embedder=embedder,
    )
    new_knowledge.load(save_path)
    print("✓ 知识加载完成")
    print(f"  加载的标题: {new_knowledge.data.title}")
    print(f"  加载的字段数: {new_knowledge.size()}")

    # 10. 测试长文本提取（分块）
    print("\n[9] 测试长文本提取（自动分块）...")
    long_text = sample_text * 5  # 重复文本模拟长文本
    knowledge.clear()
    result = knowledge.extract(long_text)
    print(f"✓ 长文本提取完成: {result}")

    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
