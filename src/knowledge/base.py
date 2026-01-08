import asyncio
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict, Optional, Type, List, Callable
from datetime import datetime
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

try:
    from src.config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)


# ===================== 提取器 (Extractor) =====================


class BaseExtractor(ABC, Generic[T]):
    """
    矿工 - 无状态提取器基类。
    
    职责：从文本中提取结构化知识，不负责存储或融合。
    """

    def __init__(self, llm_client: BaseChatModel, schema_class: Type[T]):
        """
        :param llm_client: LangChain 的 ChatModel 实例
        :param schema_class: 期望的返回 Schema 类（必须继承 BaseModel）
        """
        self.llm_client = llm_client
        self.schema_class = schema_class
    @abstractmethod
    async def aparse(self, text: str, **kwargs) -> T:
        """
        异步解析文本，返回单个知识对象。
        
        :param text: 输入文本
        :return: 解析后的知识对象
        """
        pass

    def parse(self, text: str, **kwargs) -> T:
        """
        同步解析（子类可覆盖为真正的同步实现）。
        
        默认行为：需要在异步上下文中调用 aparse。
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError("Cannot use parse() in async context. Use aparse() instead.")
            return loop.run_until_complete(self.aparse(text, **kwargs))
        except RuntimeError:
            raise

    async def batch_parse(self, texts: List[str], **kwargs) -> List[T]:
        """
        批量解析多个文本。
        
        :param texts: 文本列表
        :return: 解析结果列表
        """
        tasks = [self.aparse(text, **kwargs) for text in texts]
        return await asyncio.gather(*tasks)

    async def batch_parse_concurrent(
        self,
        texts: List[str],
        max_concurrent: int = 5,
        **kwargs
    ) -> List[T]:
        """
        带并发限制的批量解析。
        
        :param texts: 文本列表
        :param max_concurrent: 最大并发数
        :return: 解析结果列表
        """
        from asyncio import Semaphore

        semaphore = Semaphore(max_concurrent)

        async def limited_parse(text: str) -> T:
            async with semaphore:
                return await self.aparse(text, **kwargs)

        tasks = [limited_parse(text) for text in texts]
        return await asyncio.gather(*tasks)





# ===================== 集合/容器 (Collection) =====================


class BaseCollection(ABC, Generic[T]):
    """
    仓库 - 有状态集合基类。
    
    职责：存储知识点、融合去重、演化优化、序列化。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        schema_class: Type[T],
        storage: str = "memory",
        **kwargs,
    ):
        """
        :param llm_client: LLM 实例（用于演化等操作）
        :param embedder: 向量化器实例（用于语义搜索等）
        :param schema_class: 容器持有的知识 Schema 类
        :param storage: 存储后端类型（"memory"、"postgres" 等）
        """
        self.llm_client = llm_client
        self.embedder = embedder
        self.schema_class = schema_class
        self.storage = storage
        self.metadata: Dict[str, Any] = {}

    # ================= 存储层 =================

    @abstractmethod
    async def add(self, item_id: str, item: T, **kwargs):
        """
        添加知识点。
        
        :param item_id: 唯一标识符
        :param item: 知识对象
        """
        pass

    @abstractmethod
    async def remove(self, item_id: str, **kwargs) -> bool:
        """
        删除知识点。
        
        :return: 是否成功删除
        """
        pass

    @abstractmethod
    async def update(self, item_id: str, item: T, **kwargs):
        """
        更新知识点。
        
        :param item_id: 知识点 ID
        :param item: 新的知识对象
        """
        pass

    @abstractmethod
    def get(self, item_id: str) -> Optional[T]:
        """获取单个知识点"""
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        """列出所有知识点"""
        pass

    @abstractmethod
    def search(self, filter_fn: Callable[[T], bool]) -> List[T]:
        """
        按条件查询知识点。
        
        :param filter_fn: 过滤函数
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """返回容器中知识点的数量"""
        pass

    # ================= 融合层 =================

    @abstractmethod
    async def aggregate(self, items: List[T], **kwargs) -> Dict[str, Any]:
        """
        融合多个知识点。
        
        职责：清洗、去重、合并。
        
        :param items: 新提取的知识点列表
        :return: 融合统计信息（去重数、合并数等）
        """
        pass

    async def fuse_batch(self, new_items: List[T], iteration: int = 0) -> Dict[str, Any]:
        """
        融合一批新知识点到容器中。
        
        :param new_items: 新提取的知识点
        :param iteration: 迭代号
        :return: 融合统计信息
        """
        start_time = datetime.now()

        try:
            # 应用融合策略
            stats = await self.aggregate(new_items, iteration=iteration)

            stats["timestamp"] = start_time.isoformat()
            stats["duration_ms"] = (datetime.now() - start_time).total_seconds() * 1000
            stats["iteration"] = iteration

            logger.info(f"Fused batch: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error during fuse_batch: {e}")
            raise

    # ================= 演化层 =================

    @abstractmethod
    async def evolve(self, **kwargs) -> Dict[str, Any]:
        """
        演化内部知识。
        
        职责：推理新关系、剪枝低置信度、聚类等高级操作。
        
        :return: 演化统计信息
        """
        pass

    # ================= 高级流程 =================

    async def iterative_fuse_and_parse(
        self,
        extractor: "BaseExtractor[T]",
        texts: List[str],
        max_iterations: int = 3,
        convergence_threshold: float = 0.95,
    ) -> Dict[str, Any]:
        """
        迭代提取与融合流程。
        
        流程：
        1. 第一次提取：从文本中提取所有知识点
        2. 融合去重
        3. 演化优化
        4. 重复直到收敛或达到最大迭代数
        
        :param extractor: 知识提取器
        :param texts: 输入文本列表
        :param max_iterations: 最大迭代数
        :param convergence_threshold: 收敛阈值
        :return: 迭代结果摘要
        """
        iteration = 0
        previous_size = 0
        fusion_stats = []

        while iteration < max_iterations:
            logger.info(f"Iteration {iteration}: extracting...")

            # 1. 提取新知识
            extracted = await extractor.batch_parse(texts)

            # 2. 融合
            logger.info(f"Iteration {iteration}: fusing...")
            fuse_result = await self.fuse_batch(extracted, iteration)
            fusion_stats.append(fuse_result)

            # 3. 演化
            logger.info(f"Iteration {iteration}: evolving...")
            evolve_result = await self.evolve(iteration=iteration)

            # 4. 检查收敛
            current_size = self.size()
            logger.info(f"Iteration {iteration}: size={current_size}")

            if previous_size > 0:
                growth_rate = (current_size - previous_size) / previous_size
                if growth_rate < (1 - convergence_threshold):
                    logger.info(
                        f"Converged at iteration {iteration} (growth_rate={growth_rate})"
                    )
                    break

            previous_size = current_size
            iteration += 1

            await asyncio.sleep(0.1)

        return {
            "final_iteration": iteration,
            "total_items": self.size(),
            "fusion_history": fusion_stats,
        }

    # ================= 序列化 =================

    @abstractmethod
    def dump(self, format: str = "json") -> Any:
        """
        导出容器内的知识。
        
        :param format: 格式 ("json", "dict" 等)
        """
        pass

    @abstractmethod
    def load(self, data: Any, **kwargs):
        """
        从外部数据恢复知识。
        
        :param data: 外部数据 (dict, json string 或文件路径)
        """
        pass

    def clear(self):
        """清空所有知识点（可选实现）"""
        pass


# ===================== 通用实现 =====================



