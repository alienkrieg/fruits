import numpy as np

from fruits.preparation.abstract import DataPreparateur

class LAG(DataPreparateur):
    """DataPreparateur: Lag

    This preparateur adds more dimensions to each given time series.
    For every dimension, a lagged version of the dimension is appended
    to the time series. The lagged series is the original series shifted
    to right by a given number ``lag`` and cropped at the end. The first
    ``lag`` numbers are set to zero.

    :param lag: Number of indices the first element of each time series
        dimension is shifted to the right., defaults to 1
    :type lag: int, optional
    """
    def __init__(self, lag: int = 1):
        super().__init__("Lag")
        if not isinstance(lag, int) or lag <= 0:
            raise ValueError("lag has to be a integer > 0")
        self._lag = lag

    def prepare(self, X: np.ndarray) -> np.ndarray:
        """Returns the transformed dataset.

        :type X: np.ndarray
        :rtype: np.ndarray
        """
        X_new = np.zeros((X.shape[0], 2*X.shape[1], X.shape[2]))
        for i in range(X.shape[1]):
            X_new[:, 2*i, :] = X[:, i, :]
            X_new[:, 2*i+1, :] = np.roll(X[:, i, :], self._lag, axis=1)
            X_new[:, 2*i+1, :self._lag] = 0
        return X_new

    def copy(self) -> "LAG":
        """Returns a copy of this preparateur.

        :rtype: LAG
        """
        return LAG(self._lag)

    def __eq__(self, other) -> bool:
        return False

    def __str__(self) -> str:
        return f"LAG(lag={self._lag})"

    def __repr__(self) -> str:
        return "fruits.preparation.dimension.LAG"
