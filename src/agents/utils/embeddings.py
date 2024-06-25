from openai import OpenAI
from enum import Enum
from abc import ABC, abstractmethod
from typing import Union, Any, Generic, List, TypeVar

T = TypeVar("T")

embedding_model_is_load = False
embedding_model = None


def get_embedding(sentence: str):
    global embedding_model_is_load
    global embedding_model

    if not embedding_model_is_load:
        embedding_model = OpenAIEmbedding()
        embedding_model_is_load = True

    sentence = sentence.replace("\n", " ")
    embed = embedding_model.embed_list(objs=sentence)
    return embed


class EmbeddingModelType(Enum):
    SMALL_3 = "text-embedding-3-small"
    LARGE_3 = "text-embedding-3-large"
    ADA_2 = "text-embedding-ada-002"

    @property
    def is_openai(self) -> bool:
        r"""Returns whether this type of models is an OpenAI-released model."""
        return self in {
            EmbeddingModelType.SMALL_3,
            EmbeddingModelType.LARGE_3,
            EmbeddingModelType.ADA_2,
        }

    @property
    def output_dim(self) -> int:
        if self is EmbeddingModelType.SMALL_3:
            return 1536
        elif self is EmbeddingModelType.LARGE_3:
            return 3072
        elif self is EmbeddingModelType.ADA_2:
            return 1536
        else:
            raise ValueError(f"Unknown model type {self}.")


class BaseEmbedding(ABC, Generic[T]):
    r"""Abstract base class for text embedding functionalities."""

    @abstractmethod
    def embed_list(
        self,
        objs: List[T],
        **kwargs: Any,
    ) -> List[List[float]]:
        r"""Generates embeddings for the given texts.

        Args:
            objs (List[T]): The objects for which to generate the embeddings.
            **kwargs (Any): Extra kwargs passed to the embedding API.

        Returns:
            List[List[float]]: A list that represents the
            generated embedding as a list of floating-point numbers or a
            numpy matrix with embeddings.
        """
        pass

    def embed(
        self,
        obj: T,
        **kwargs: Any,
    ) -> List[float]:
        r"""Generates an embedding for the given text.

        Args:
            obj (T): The object for which to generate the embedding.
            **kwargs (Any): Extra kwargs passed to the embedding API.

        Returns:
            List[float]: A list of floating-point numbers representing the
                generated embedding.
        """
        return self.embed_list([obj], **kwargs)[0]

    @abstractmethod
    def get_output_dim(self) -> int:
        r"""Returns the output dimension of the embeddings.

        Returns:
            int: The dimensionality of the embedding for the current model.
        """
        pass


class OpenAIEmbedding(BaseEmbedding[str]):
    r"""Provides text embedding functionalities using OpenAI's models.

    Args:
        model (OpenAiEmbeddingModel, optional): The model type to be used for
            generating embeddings. (default: :obj:`ModelType.SMALL_3`)

    Raises:
        RuntimeError: If an unsupported model type is specified.
    """

    def __init__(
        self,
        model_type: EmbeddingModelType = EmbeddingModelType.SMALL_3,
    ) -> None:
        if not model_type.is_openai:
            raise ValueError("Invalid OpenAI embedding model type.")
        self.model_type = model_type
        self.output_dim = model_type.output_dim
        self.client = OpenAI()

    def embed_list(
        self,
        objs: Union[str, List[str]],
        **kwargs: Any,
    ) -> List[List[float]]:
        r"""Generates embeddings for the given texts.

        Args:
            objs (List[str]): The texts for which to generate the embeddings.
            **kwargs (Any): Extra kwargs passed to the embedding API.

        Returns:
            List[List[float]]: A list that represents the generated embedding
                as a list of floating-point numbers.
        """
        # TODO: count tokens
        response = self.client.embeddings.create(
            input=objs,
            model=self.model_type.value,
            **kwargs,
        )
        return [data.embedding for data in response.data]

    def get_output_dim(self) -> int:
        r"""Returns the output dimension of the embeddings.

        Returns:
            int: The dimensionality of the embedding for the current model.
        """
        return self.output_dim
