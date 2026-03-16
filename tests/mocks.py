"""Mock implementations for LLM and Embeddings for testing without API keys."""

from typing import Any, List, Optional, Type, get_origin, get_args
from pydantic import BaseModel, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableSerializable, RunnableConfig


class MockEmbeddings(Embeddings):
    """Mock Embeddings that returns deterministic vectors based on str hash."""

    def __init__(self, dim: int = 768):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return deterministic embedding vectors based on text hash."""
        return [self._hash_to_vector(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Return deterministic embedding vector for query."""
        return self._hash_to_vector(text)

    def _hash_to_vector(self, text: str) -> List[float]:
        """Convert text to deterministic vector of given dimension."""
        hash_val = hash(text)
        # Create deterministic values based on hash
        return [(hash_val + i) % 1000 / 1000.0 for i in range(self.dim)]


class MockStructuredRunnable(RunnableSerializable):
    """
    Mock Runnable that simulates with_structured_output behavior.
    Generates dummy data matching the given Pydantic schema.
    """

    schema: Type[BaseModel]

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self, input: Any, config: Optional[RunnableConfig] = None
    ) -> BaseModel:
        """Generate and return a mock instance of the schema."""
        return self._generate_mock_instance(self.schema)

    def batch(
        self,
        inputs: List[Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[BaseModel]:
        """Generate mock instances for batch input."""
        return [self.invoke(inp, config) for inp in inputs]

    def _generate_mock_instance(self, model_cls: Type[BaseModel]) -> BaseModel:
        """Recursively generate mock instance matching schema."""
        data = {}

        for field_name, field_info in model_cls.model_fields.items():
            field_type = field_info.annotation

            # Handle Optional types
            origin = get_origin(field_type)
            if origin is Optional.__class__ or (
                hasattr(field_type, "__args__") and type(None) in get_args(field_type)
            ):
                # Extract the actual type from Optional
                args = get_args(field_type)
                field_type = args[0] if args else str

            origin = get_origin(field_type)

            # Handle List types
            if origin is list:
                args = get_args(field_type)
                if args and issubclass(args[0], BaseModel):
                    # List of Pydantic models
                    data[field_name] = [self._generate_mock_instance(args[0])]
                else:
                    # List of primitives or empty
                    data[field_name] = []

            # Handle Pydantic model fields
            elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                data[field_name] = self._generate_mock_instance(field_type)

            # Handle primitive types
            elif field_type == str:
                data[field_name] = f"mock_{field_name}"
            elif field_type == int:
                data[field_name] = 1
            elif field_type == float:
                data[field_name] = 1.0
            elif field_type == bool:
                data[field_name] = True
            else:
                # Default to None for unknown types
                data[field_name] = None

        return model_cls(**data)


class MockChatModel(BaseChatModel):
    """Mock Chat Model for testing without API calls."""

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Generate mock response."""
        # Return a simple mock message
        return type("ChatResult", (), {"generations": [type("Generation", (), {"message": AIMessage(content="mock response")})]})()

    def with_structured_output(self, schema: Type[BaseModel], **kwargs: Any) -> RunnableSerializable:
        """
        Return a MockStructuredRunnable that generates mock data matching the schema.
        This simulates LangChain's with_structured_output behavior.
        """
        runnable = MockStructuredRunnable(schema=schema)
        return runnable
