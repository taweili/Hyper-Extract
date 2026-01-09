"""
GenericKnowledge 向量搜索功能演示

展示如何使用新的向量索引功能进行语义搜索。
"""

from pydantic import BaseModel, Field
from typing import List


# ==================== 1. 定义 Schema ====================

class Article(BaseModel):
    """文章 Schema"""
    title: str = Field(description="文章标题")
    author: str = Field(description="作者")
    content: str = Field(description="文章内容摘要")
    tags: List[str] = Field(default_factory=list, description="标签")


# ==================== 2. 初始化 Knowledge ====================

async def main():
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from src.knowledge.generic import GenericKnowledge
    
    # 初始化
    knowledge = GenericKnowledge(
        llm_client=ChatOpenAI(model="gpt-4"),
        embedder=OpenAIEmbeddings(),
        schema_class=Article,
        prompt="Extract article information:",
        max_workers=5,
        show_progress=True
    )
    
    # ==================== 3. 提取知识 ====================
    
    text = """
    人工智能的发展历程
    作者：张三
    
    人工智能(AI)从1956年达特茅斯会议诞生至今，经历了多次起伏。
    深度学习的突破使得AI在图像识别、自然语言处理等领域取得巨大进展。
    
    大语言模型的崛起
    作者：李四
    
    2023年，ChatGPT的发布标志着大语言模型时代的到来。
    这些模型能够理解和生成人类语言，应用范围广泛。
    """
    
    stats = knowledge.extract(text)
    print(f"✅ 提取完成：{stats}")
    print(f"📊 共提取 {knowledge.size()} 篇文章\n")
    
    # ==================== 4. 向量搜索 ====================
    
    print("🔍 开始语义搜索...")
    
    # 搜索 1：关于深度学习
    results = knowledge.search("深度学习和神经网络", top_k=2)
    print("\n查询：'深度学习和神经网络'")
    for i, article in enumerate(results, 1):
        print(f"  {i}. {article.title} - {article.author}")
    
    # 搜索 2：关于 ChatGPT
    results = knowledge.search("ChatGPT 语言模型", top_k=2)
    print("\n查询：'ChatGPT 语言模型'")
    for i, article in enumerate(results, 1):
        print(f"  {i}. {article.title} - {article.author}")
    
    # ==================== 5. 持久化 ====================
    
    # 保存
    knowledge.dump("knowledge_data.json")
    print("\n💾 已保存到 knowledge_data.json")
    
    # 清空并重新加载
    knowledge.clear()
    print(f"🗑️  清空后数量：{knowledge.size()}")
    
    knowledge.load("knowledge_data.json")
    print(f"📥 加载后数量：{knowledge.size()}")
    
    # 加载后搜索仍然有效（索引会自动重建）
    results = knowledge.search("AI 发展", top_k=1)
    print(f"\n🔍 加载后搜索：找到 {len(results)} 条结果")


# ==================== 6. 架构说明 ====================

"""
## 📐 架构设计

### BaseKnowledge（模板方法模式）
- `_vector_store`: 向量数据库实例（FAISS）
- `_index_dirty`: 脏标记，追踪数据变化
- `build_index()`: 模板方法，统一索引构建流程
- `_data_to_documents()`: 抽象钩子，子类实现转换逻辑

### GenericKnowledge（具体实现）
1. **_data_to_documents()**: 将 self._items 转为 Document 列表
2. **merge()**: 添加数据后设置 `self._index_dirty = True`
3. **search()**: 
   - 调用 `build_index()` 确保索引最新
   - 使用 `_vector_store.similarity_search()`
   - 从 metadata 恢复原始对象
4. **clear()**: 清空数据并重置索引

### 工作流程
```
提取 → merge (设置 dirty=True) → search (自动 build_index) → 返回结果
```

### 优势
✅ 延迟索引：只在需要时构建
✅ 自动重建：数据变化后搜索时自动更新
✅ 可插拔后端：FAISS/Qdrant/Chroma 等
✅ 持久化友好：load 后自动标记 dirty
"""

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
