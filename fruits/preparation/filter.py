import numpy as np

from fruits.preparation.abstract import DataPreparateur

class DIL(DataPreparateur):
    """DataPreparateur: Dilation

    This preparateur sets some slices in each time series in the
    given dataset to zero. The indices and lengths for those zero
    sequences are chosen randomly.

    :param clusters: Float value between 0 and 1 (incl.). The number of
        zero strips will be calculated by multiplying
        ``clusters * X.shape[2]`` in ``self.fit(X)``., defaults to 0.01
    :type clusters: float, optional
    """
    def __init__(self,
                 clusters: float = 0.01):
        super().__init__("Dilation")
        self._clusters = clusters
        self._indices = None
        self._lengths = None
    
    def fit(self, X: np.ndarray):
        """Fits the preparateur to the given dataset by randomizing the
        starting points and lengths of the zero strips.

        :type X: np.ndarray
        """
        nclusters = int(self._clusters * X.shape[2])
        self._indices = sorted(np.random.random_sample(nclusters))
        self._lengths = []
        for i in range(len(self._indices)):
            if i == len(self._indices)-1:
                b = 1 - self._indices[i]
            else:
                b = self._indices[i+1] - self._indices[i]
            self._lengths.append(b*np.random.random_sample())
            
    def prepare(self, X: np.ndarray) -> np.ndarray:
        """Returns the transformed dataset.

        :type X: np.ndarray
        :rtype: np.ndarray
        :raises: RuntimeError if self.fit() wasn't called
        """
        if self._indices is None:
            raise RuntimeError("Missing call of fit method")
        X_new = X.copy()
        for i in range(len(self._indices)):
            start = int(self._indices[i] * X.shape[2])
            length = int(self._lengths[i] * X.shape[2])
            X_new[:, :, start:start+length] = 0
        return X_new
    
    def copy(self) -> "DIL":
        """Returns a copy of this preparateur.

        :rtype: DIL
        """
        return DIL(self._clusters)

    def __eq__(self, other) -> bool:
        return False

    def __str__(self) -> str:
        return f"DIL(clusters={self._clusters})"

    def __repr__(self) -> str:
        return "fruits.preparation.filter.DIL"


class WIN(DataPreparateur):
    """DataPreparateur: Window

    Outside of a certain window the time series is set to zero.
    The window is obtained according to 'quantiles' of a certain
    function of each time series, for example its quadratic variation by
    calculating increments and getting results from
    ``fruits.core.ISS(X, [SimpleWord("[11]")])``.

    :param start: Quantile start; float value between 0 and 1 (incl.).
    :type start: float
    :param end: Quantile end; float value between 0 and 1 (incl.).
    :type end: float
    """
    def __init__(self,
                 start: float,
                 end: float):
        super().__init__("Window")
        self._start = start
        self._end = end
        self._requisite = "INC -> [11]"
            
    def prepare(self, X: np.ndarray) -> np.ndarray:
        """Returns the transformed dataset.

        :type X: np.ndarray
        :rtype: np.ndarray
        """
        Q = self._get_requisite(X)

        maxima = np.expand_dims(np.max(Q, axis=2), axis=-1)
        Q = Q / maxima

        mask = (Q >= self._start) & (Q <= self._end)
        return X * mask
    
    def copy(self) -> "WIN":
        """Returns a copy of this preparateur.

        :rtype: WIN
        """
        return WIN(self._start, self._end)

    def __eq__(self, other) -> bool:
        if not isinstance(other, WIN):
            raise TypeError(f"Cannot compare WIN with type {type(other)}")
        return (self._start == other._start and
                self._end == other._end)

    def __str__(self) -> str:
        return f"WIN(start={self._start}, end={self._end})"

    def __repr__(self) -> str:
        return "fruits.preparation.filter.WIN"


class DOT(DataPreparateur):
    """DataPreparateur: Dotting

    Keeps every n-th point of a time series while setting everything
    else to a given value.

    :param n_prop: Used for calculation of ``n=n_prop*X.shape[2]``.
        Has to be a float in (0, 1)., defaults to 0.1
    :type n_prop: float, optional
    :param value: New value for the other points., defaults to 0
    :type value: float, optional
    """
    def __init__(self, n_prop: float = 0.1, value: float = 0):
        super().__init__("Dotting")
        if not 0 < n_prop < 1:
            raise ValueError("Argument 'n_prop' has to be in interval (0, 1)")
        self._n_prop = n_prop
        self._value = value

    def prepare(self, X: np.ndarray):
        """Returns the transformed dataset.

        :type X: np.ndarray
        :rtype: np.ndarray
        """
        out = np.ones(X.shape) * self._value
        n = int(self._n_prop * X.shape[2])
        if n <= 0:
            n = 1
        out[:, :, n-1::n] = X[:, :, n-1::n]
        return out
    
    def copy(self) -> "DOT":
        """Returns a copy of this preparateur.

        :rtype: DOT
        """
        return DOT(self._n_prop, self._value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, DOT):
            raise TypeError(f"Cannot compare DOT with type {type(other)}")
        return (self._n_prop == other._n_prop and self._value == other._value)

    def __str__(self) -> str:
        return f"DOT(n_prop={self._n_prop}, value={self._value})"

    def __repr__(self) -> str:
        return "fruits.preparation.filter.DOT"
