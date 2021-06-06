from abc import ABC, abstractmethod

import numpy as np

from fruits import _accelerated

class DataPreparateur(ABC):
    """Abstract class DataPreperateur
    
    A DataPreparateur object can be fitted on a three dimensional numpy 
    array. The output of DataPreparateur.prepare is a numpy array that
    matches the shape of the input array.
    """
    def __init__(self, name: str = ""):
        super().__init__()
        self.name = name

    @property
    def name(self) -> str:
        """Simple identifier for this object."""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    def copy(self):
        """Returns a copy of the DataPreparateur object.
        
        :returns: Copy of this object
        :rtype: DataPreparateur
        """
        dp = DataPreparateur(self.name)
        return dp

    def fit(self, X: np.ndarray):
        """Fits the DataPreparateur to the given dataset.
        
        :param X: (multidimensional) time series dataset
        :type X: np.ndarray
        """
        pass

    @abstractmethod
    def prepare(self, X: np.ndarray) -> np.ndarray:
        pass

    def fit_prepare(self, X: np.ndarray) -> np.ndarray:
        """Fits the given dataset to the DataPreparateur and returns
        the preparated results.
        
        :param X: (multidimensional) time series dataset
        :type X: np.ndarray
        """
        self.fit(X)
        return self.prepare(X)

    def __copy__(self):
        return self.copy()

    def __repr__(self) -> str:
        return "DataPreparateur('" + self._name + "')"


class INC(DataPreparateur):
    """DataPreparateur: Increments
    
    For a time series 
    `X = [x_1, x_2, ..., x_n]`
    this class produces the output
    `X_inc = [0, x_2-x_1, x_3-x_2, ..., x_n-x_{n-1}]`.
    If `zero_padding` is set to `False`, then the 0 above will be
    replaced by `x_1`.
    """
    def __init__(self,
                 zero_padding: bool = True,
                 name: str = "Increments"):
        super().__init__(name)
        self._zero_padding = zero_padding

    def prepare(self, X: np.ndarray) -> np.ndarray:
        """Returns the increments of all time series in X.
        This is the equivalent of the convolution of X and [-1,1].
        
        :param X: (multidimensional) time series dataset
        :type X: np.ndarray
        :returns: stepwise slopes of each time series in X
        :rtype: np.ndarray
        """
        out = _accelerated._increments(X)
        if self._zero_padding:
            out[:, :, 0] = 0
        return out

    def copy(self):
        """Returns a copy of the DataPreparateur object.
        
        :returns: Copy of this object
        :rtype: INC
        """
        dp = INC(self._zero_padding, self.name)
        return dp


class STD(DataPreparateur):
    """DataPreparateur: Standardization
    
    For a time series `X` this class produces the output
    `X_std = (X-mean(X))/std(X)`.
    """
    def __init__(self,
                 name: str = "Standardization"):
        super().__init__(name)
        self._means = None
        self._stds = None

    def prepare(self, X: np.ndarray) -> np.ndarray:
        """Returns (X_ij-mu)/v for each time series i and all of its
        dimensions j where mu is the calculated mean and v is the
        standard deviation of this dimension.
        
        :param X: (multidimensional) time series dataset
        :type X: np.ndarray
        :returns: (standardized) dataset
        :rtype: np.ndarray
        :raises: RuntimeError if self.fit() wasn't called
        """
        self._means = np.mean(X, axis=2)
        self._stds = np.std(X, axis=2)
        out = X.copy()
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                out[i, j, :] -= self._means[i, j]
                out[i, j, :] /= self._stds[i, j]
        return out

    def copy(self):
        """Returns a copy of the DataPreparateur object.
        
        :returns: Copy of this object
        :rtype: STD
        """
        dp = STD(self.name)
        return dp
