from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List

DEFAULT_TOP_K_RESULTS = 1


class BaseRetriever(ABC):
    r"""Abstract base class for implementing various types of information
    retrievers.
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def process(self, content_input_path: str, **kwargs: Any) -> None:
        r"""
        Processes content. Subclasses should implement this
        method according to their specific needs.

        Args:
            content_input_path (str): The path or URL of the content to
                process.
            **kwargs (Any): Flexible keyword arguments for additional
                parameters.
        """
        pass

    @abstractmethod
    def query(
        self, query: str, top_k: int = DEFAULT_TOP_K_RESULTS, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        r"""Query the results. Subclasses should implement this
        method according to their specific needs.

        Args:
            query (str): Query string for information retriever.
            top_k (int, optional): The number of top results to return during
                retriever. Must be a positive integer. Defaults to
                `DEFAULT_TOP_K_RESULTS`.
            **kwargs (Any): Flexible keyword arguments for additional
                parameters, like `similarity_threshold`.
        """
        pass
