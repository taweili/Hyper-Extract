"""
测试 BaseAutoType 类的功能。
"""
import pytest
from typing import List, Optional
from pydantic import BaseModel, Field
from unittest.mock import MagicMock, AsyncMock
import json

from hyperextract.core import BaseAutoType


# 定义测试用的 Schema
class Article(BaseModel):
    """文章 Schema"""
    title: str = Field(..., description="文章标题")
    authors: List[str] = Field(default_factory=list, description="作者列表")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    summary: str = Field(default="", description="摘要")


class Person(BaseModel):
    """人物 Schema"""
    name: str = Field(..., description="人物名字")
    age: int = Field(..., description="年龄")
    occupation: str = Field(default="", description="职业")


@pytest.fixture
def mock_llm():
    """创建 mock LLM 客户端"""
    llm = AsyncMock()
    return llm


@pytest.fixture
def mock_embedder():
    """创建 mock Embeddings 客户端"""
    embedder = MagicMock()
    return embedder


@pytest.fixture
def a_article(mock_llm, mock_embedder):
    """创建一个 Article 类型的 BaseAutoType 实例"""
    return BaseAutoType(
        llm_client=mock_llm,
        embedder=mock_embedder,
        schema_class=Article,
        storage="memory",
    )


@pytest.fixture
def a_person(mock_llm, mock_embedder):
    """创建一个 Person 类型的 BaseAutoType 实例"""
    return BaseAutoType(
        llm_client=mock_llm,
        embedder=mock_embedder,
        schema_class=Person,
        storage="memory",
    )


class TestBaseAutoTypeInitialization:
    """测试 BaseAutoType 类的初始化"""

    def test_auto_type_init_with_article_schema(self, a_article):
        """测试使用 Article schema 初始化"""
        assert a_article.schema_class == Article
        assert a_article.storage == "memory"
        assert a_article.data is not None

    def test_auto_type_init_with_initial_data(self, mock_llm, mock_embedder):
        """测试带初始数据的初始化"""
        initial_article = Article(
            title="Test Article",
            authors=["Author 1"],
            keywords=["test"],
            summary="A test article"
        )
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
            initial_data=initial_article,
        )
        assert knowledge.data == initial_article
        assert knowledge.data.title == "Test Article"

    def test_auto_type_with_different_schemas(self, mock_llm, mock_embedder):
        """测试使用不同 Schema 的 BaseAutoType"""
        article_k = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
        )
        person_k = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Person,
        )
        assert article_k.schema_class == Article
        assert person_k.schema_class == Person


class TestBaseAutoTypeExtract:
    """测试 BaseAutoType 的 extract 方法"""

    @pytest.mark.asyncio
    async def test_extract_article(self, a_article, mock_llm):
        """测试提取文章信息"""
        # 模拟 LLM 返回的响应（with_structured_output 直接返回对象）
        expected_article = Article(
            title="AI in 2024",
            authors=["John Doe", "Jane Smith"],
            keywords=["AI", "Machine Learning"],
            summary="An overview of AI trends in 2024"
        )
        
        # 模拟 with_structured_output 返回的 structured_llm
        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = expected_article
        mock_llm.with_structured_output.return_value = mock_structured_llm

        text = "Artificial Intelligence continues to advance in 2024..."
        result = await a_article.extract(text)

        assert result.title == "AI in 2024"
        assert len(result.authors) == 2
        assert "AI" in result.keywords
        assert a_article.data == result

    @pytest.mark.asyncio
    async def test_extract_with_markdown_response(self, a_article, mock_llm):
        """测试 with_structured_output 自动处理响应格式"""
        # 使用 with_structured_output 无需处理 markdown 格式
        expected_article = Article(
            title="Test Article",
            authors=["Author"],
            keywords=["test"],
            summary="Summary"
        )
        
        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = expected_article
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await a_article.extract("test text")
        assert result.title == "Test Article"
        assert result.authors[0] == "Author"

    @pytest.mark.asyncio
    async def test_aextract_calls_extract(self, a_article, mock_llm):
        """测试 aextract 方法调用 extract"""
        expected_article = Article(
            title="Test",
            authors=[],
            keywords=[],
            summary=""
        )
        
        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = expected_article
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await a_article.aextract("test")
        assert result.title == "Test"


class TestBaseAutoTypeDump:
    """测试 BaseAutoType 的 dump 方法"""

    def test_dump_to_json(self, mock_llm, mock_embedder):
        """测试导出为 JSON 格式"""
        article = Article(
            title="Test",
            authors=["Alice"],
            keywords=["test"],
            summary="A test"
        )
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
            initial_data=article,
        )

        json_str = knowledge.dump(format="json")
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["title"] == "Test"
        assert parsed["authors"] == ["Alice"]

    def test_dump_to_dict(self, mock_llm, mock_embedder):
        """测试导出为字典格式"""
        article = Article(
            title="Test",
            authors=["Alice"],
            keywords=["test"],
            summary="A test"
        )
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
            initial_data=article,
        )

        data_dict = knowledge.dump(format="dict")
        assert isinstance(data_dict, dict)
        assert data_dict["title"] == "Test"


class TestBaseAutoTypeLoad:
    """测试 BaseAutoType 的 load 方法"""

    def test_load_from_dict(self, mock_llm, mock_embedder):
        """测试从字典加载"""
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
        )

        data = {
            "title": "Loaded Article",
            "authors": ["Author1"],
            "keywords": ["loaded"],
            "summary": "Loaded from dict"
        }
        knowledge.load(data)

        assert knowledge.data.title == "Loaded Article"
        assert knowledge.data.authors == ["Author1"]

    def test_load_from_json_string(self, mock_llm, mock_embedder):
        """测试从 JSON 字符串加载"""
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
        )

        json_str = json.dumps({
            "title": "JSON Article",
            "authors": ["JSON Author"],
            "keywords": [],
            "summary": ""
        })
        knowledge.load(json_str)

        assert knowledge.data.title == "JSON Article"

    def test_load_invalid_data_raises_error(self, mock_llm, mock_embedder):
        """测试加载无效数据时抛出错误"""
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
        )

        # 缺少必需字段
        invalid_data = {"authors": ["Author"]}
        with pytest.raises(Exception):
            knowledge.load(invalid_data)


class TestBaseAutoTypeSearch:
    """测试 BaseAutoType 的 search 方法"""

    @pytest.mark.asyncio
    async def test_search_returns_dict(self, mock_llm, mock_embedder):
        """测试 search 返回字典格式的数据"""
        article = Article(
            title="Search Test",
            authors=["Searcher"],
            keywords=["search"],
            summary="Testing search"
        )
        knowledge = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
            initial_data=article,
        )

        result = await knowledge.search("search")
        assert isinstance(result, dict)
        assert result["title"] == "Search Test"


class TestBaseAutoTypeEvolve:
    """测试 BaseAutoType 的 evolve 和 aevolve 方法"""

    @pytest.mark.asyncio
    async def test_aevolve_default_implementation(self, a_article):
        """测试 aevolve 的默认实现（不做任何操作）"""
        await a_article.aevolve()
        # 如果没有抛出异常，则测试通过


class TestBaseAutoTypeMultipleSchemas:
    """测试使用多个不同 Schema 的场景"""

    def test_different_schemas_independent(self, mock_llm, mock_embedder):
        """测试不同 Schema 的 BaseAutoType 相互独立"""
        article_k = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Article,
        )
        person_k = BaseAutoType(
            llm_client=mock_llm,
            embedder=mock_embedder,
            schema_class=Person,
        )

        # 分别为两个 knowledge 加载数据
        article_data = {
            "title": "Article",
            "authors": [],
            "keywords": [],
            "summary": ""
        }
        person_data = {
            "name": "John",
            "age": 30,
            "occupation": "Engineer"
        }

        article_k.load(article_data)
        person_k.load(person_data)

        # 验证数据相互独立
        assert article_k.data.title == "Article"
        assert person_k.data.name == "John"
        assert isinstance(article_k.data, Article)
        assert isinstance(person_k.data, Person)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
