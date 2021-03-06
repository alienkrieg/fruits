from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class DataPreparateur(ABC):
    """Abstract class for a data preparateur.

    A preparateur can be fitted on a three dimensional numpy array
    (preferably containing time series data). The output of
    ``self.transform`` is a numpy array that matches the shape of the
    input array.
    A class derived from DataPreparateur can be added to a
    ``fruits.Fruit`` object for the preprocessing step.

    :param name: Identification string of the feature sieve.,
        defaults to ""
    :type name: str, optional
    """

    def __init__(self, name: str = ""):
        self.name = name

    def fit(self, X: np.ndarray, **kwargs) -> None:
        """Fits the DataPreparateur to the given dataset."""

    @abstractmethod
    def transform(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Transforms the given timeseries dataset."""

    def fit_transform(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Equivalent of calling ``DataPreparateur.fit`` and
        ``DataPreparateur.transform`` consecutively.

        :param X: 2-dimensional numpy array of iterated sums.
        :type X: np.ndarray
        :rtype: np.ndarray
        """
        self.fit(X, **kwargs)
        return self.transform(X, **kwargs)

    def _get_cache_keys(self) -> dict[str, list[str]]:
        # returns keys for cache needed in the sieve
        return dict()

    @abstractmethod
    def copy(self) -> "DataPreparateur":
        pass

    def __eq__(self, other: Any) -> bool:
        return False

    def __repr__(self) -> str:
        return f"fruits.preparation.abstract.DataPreparateur('{self.name}')"
