from abc import ABC

import numpy as np


class AbstractCallback(ABC):
    """Another class inheriting ``AbstractCallback`` can overwrite one
    or more of the class methods.

    The callback can then be used in a call of
    :meth:`fruits.core.fruit.Fruit.transform`.
    """

    def on_next_branch(self):
        """Called every time the current
        :class:`~fruits.core.fruit.FruitBranch` in a
        :class:`~fruits.core.fruit.Fruit` object is switched.
        """

    def on_preparateur(self, X: np.ndarray):
        """Called after the calculation of prepared data for each
        :class:`~fruits.preparation.abstract.DataPreparateur`.

        :type X: np.ndarray
        """

    def on_preparation_end(self, X: np.ndarray):
        """Called once after the calculation of the prepared data with
        the last :class:`~fruits.preparation.abstract.DataPreparateur`.

        :type X: np.ndarray
        """

    def on_iterated_sum(self, X: np.ndarray):
        """Called for every iterated sum calculated for each single
        :class:`~fruits.words.word.Word`.

        :type X: np.ndarray
        """

    def on_sieve(self, X: np.ndarray):
        """Called after each use of a
        :class:`~fruits.sieving.abstract.FeatureSieve`.

        :type X: np.ndarray
        """

    def on_sieving_end(self, X: np.ndarray):
        """Called once at the end of the feature calculation.

        :type X: np.ndarray
        """
