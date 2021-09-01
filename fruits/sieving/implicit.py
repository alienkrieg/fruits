import numpy as np

from fruits.sieving.abstract import FeatureSieve
from fruits.preparation.backend import _increments

class PPV(FeatureSieve):
    """FeatureSieve: Proportion of positive values

    For a calculated quantile with ``PPV.fit``, this feature sieve
    calculates the proportion of values in a time series that are
    greater than the calculated quantile(s).

    :param quantile: Quantile or list of quantiles ``[q_1, ..., q_n]``
        as actual value(s) or probability for quantile calculation
        (e.g. 0.5 for the 0.5-quantile)., defaults to 0.5
    :type quantile: float or list of floats, optional
    :param constant: If ``True``, the argument ``quantile`` is
        interpreted as the actual value for the quantile.
        If ``quantile`` is a list, then ``constant`` can be a list of
        booleans ``[b_1, ..., b_n]`` where ``b_i`` explains the
        interpretation of ``q_i`` or a single boolean for each ``q_i``.
        (value or probability)., defaults to False
    :type constant: bool or list of bools, optional
    :param sample_size: Sample size to use for quantile calculation.
        This option can be ignored if ``constant`` is set to ``True``.,
        defaults to 0.05
    :type sample_size: float, optional
    :param segments: If `True`, then the proportion of values within
        each two quantiles will be calculated. If `quantile` is a list,
        then this list will be sorted and the corresponding features
        will be

        .. code-block::python
            np.array([np.sum(q_{i-1} <= X[k] < q_i)]) / len(X[k])])

        where ``k`` is the index of the time series and ``i`` ranges
        from 1 to n.
        If set to ``False``, then the features will be

        .. code-block::python
            np.array([np.sum(X[k] <= q_i)]) / len(X[k])])

        with the same index rules., defaults to False
    :type segments: bool, optional
    """
    def __init__(self,
                 quantile: float = 0.5,
                 constant: bool = False,
                 sample_size: float = 1.0,
                 segments: bool = False):
        super().__init__("Proportion of positive values")
        if isinstance(quantile, list):
            if not isinstance(constant, list):
                constant = [constant for i in range(len(quantile))]
            elif len(quantile) != len(constant):
                raise ValueError("If 'quantile' is a list, then 'constant'"+
                                 " also has to be a list of same length or"+
                                 " a single boolean.") 
            for q, c in zip(quantile, constant):
                if not c and not (0 <= q <= 1):
                    raise ValueError("If 'constant' is set to False,"+
                                     " 'quantile' has to be a value in [0,1]")
        else:
            quantile = [quantile]
            if isinstance(constant, list):
                if len(constant) > 1:
                    raise ValueError("'constant' has to be a single boolean"+
                                     " if 'quantile' is a single float")
            else:
                constant = [constant]
        if segments:
            self._q_c_input = list(zip(list(set(quantile)),constant))
            self._q_c_input = sorted(self._q_c_input, key=lambda x: x[0])
        else:
            self._q_c_input = list(zip(quantile,constant))
        self._q = None
        if not 0 < sample_size <= 1:
            raise ValueError("'sample_size' has to be a float in (0, 1]")
        self._sample_size = sample_size
        if segments and len(quantile) == 1:
            raise ValueError("If 'segments' is set to `True` then 'quantile'"+
                             " has to be a list of length >= 2.")
        self._segments = segments

    def nfeatures(self) -> int:
        """Returns the number of features this sieve produces.

        :rtype: int
        """
        if self._segments:
            return len(self._q_c_input) - 1
        else:
            return len(self._q_c_input)

    def fit(self, X: np.ndarray):
        """Calculates and remembers the quantile(s) of the input data.

        :type X: np.ndarray
        """
        self._q = [x[0] for x in self._q_c_input]
        for i in range(len(self._q)):
            if not self._q_c_input[i][1]:
                sample_size = int(self._sample_size * len(X))
                if sample_size < 1:
                    sample_size = 1
                selection = np.random.choice(np.arange(len(X)),
                                             size=sample_size,
                                             replace=False)
                self._q[i] = np.quantile(np.array(
                                            [X[i] for i in selection]
                                         ).flatten(),
                                         self._q[i])

    def sieve(self, X: np.ndarray) -> np.ndarray:
        """Returns the transformed data. See the class definition for
        detailed information.

        :type X: np.ndarray
        :returns: array of features
        :rtype: np.ndarray
        :raises: RuntimeError if ``self.fit`` wasn't called
        """
        if self._q is None:
            raise RuntimeError("Missing call of PPV.fit()")
        result = np.zeros((X.shape[0], self.nfeatures()))
        for i in range(X.shape[0]):
            if self._segments:
                for j in range(1, len(self._q)):
                    result[i, j-1] = np.sum(np.logical_and(
                                                self._q[j-1] <= X[i],
                                                X[i] < self._q[j]))
                    result[i, j-1] /= X.shape[1]
            else:
                for j in range(len(self._q)):
                    result[i, j] = np.sum((X[i] >= self._q[j]))
                    result[i, j] /= X.shape[1]
        if self.nfeatures() == 1:
            return result[:, 0]
        return result

    def copy(self) -> "PPV":
        """Returns a copy of this object.

        :rtype: PPV
        """
        fs = PPV([x[0] for x in self._q_c_input],
                 [x[1] for x in self._q_c_input],
                 self._sample_size,
                 self._segments)
        return fs

    def summary(self) -> str:
        """Returns a better formatted summary string for the sieve."""
        string = f"PPV [sampling={self._sample_size}"
        if self._segments:
            string += ", segments"
        string += f"] -> {self.nfeatures()}:"
        for x in self._q_c_input:
            string += f"\n   > {x[0]} | {x[1]}"
        return string

    def __str__(self) -> str:
        return "PPV(" + \
               f"quantile={[x[0] for x in self._q_c_input]}, " + \
               f"constant={[x[1] for x in self._q_c_input]}, " + \
               f"sample_size={self._sample_size}, " + \
               f"segments={self._segments})"


class PPVC(PPV):
    """FeatureSieve: Proportion of connected components of positive
    values

    For a calculated quantile with ``PPVC.fit``, this FeatureSieve
    calculates the connected components of the proportion of values in
    a time series that is greater than the calculated quantile.
    This is equivalent to the number of consecutive strips of 1's in
    the array ``X>=quantile``.

    :param quantile: Quantile or list of quantiles ``[q_1, ..., q_n]``
        as actual value(s) or probability for quantile calculation
        (e.g. 0.5 for the 0.5-quantile)., defaults to 0.5
    :type quantile: float or list of floats, optional
    :param constant: If ``True``, the argument ``quantile`` is
        interpreted as the actual value for the quantile.
        If ``quantile`` is a list, then ``constant`` can be a list of
        booleans ``[b_1, ..., b_n]`` where ``b_i`` explains the
        interpretation of ``q_i`` or a single boolean for each ``q_i``.
        (value or probability)., defaults to False
    :type constant: bool or list of bools, optional
    :param sample_size: Sample size to use for quantile calculation.
        This option can be ignored if ``constant`` is set to ``True``.,
        defaults to 0.05
    :type sample_size: float, optional
    """
    def __init__(self,
                 quantile: float = 0.5,
                 constant: bool = False,
                 sample_size: float = 1.0):
        super().__init__(quantile,
                         constant,
                         sample_size,
                         False)
        self.name = "Proportion of connected components of positive values"

    def sieve(self, X: np.ndarray) -> np.ndarray:
        """Returns the transformed data. See the class definition for
        detailed information.

        :type X: np.ndarray
        :returns: Array of features.
        :rtype: np.ndarray
        :raises: RuntimeError if ``self.fit`` wasn't called
        """
        if self._q is None:
            raise RuntimeError("Missing call of PPVC.fit()")
        result = np.zeros((X.shape[0], self.nfeatures()))
        for i in range(len(self._q)):
            diff = _increments(np.expand_dims(
                                (X >= self._q[i]).astype(np.int32),
                                axis=1))[:, 0, :]
            # at most X.shape[1]/2 connected components are possible
            result[:, i] = 2*np.sum(diff == 1, axis=-1) / X.shape[1]
        if self.nfeatures() == 1:
            return result[:, 0]
        return result

    def copy(self) -> "PPVC":
        """Returns a copy of this object.

        :rtype: PPVC
        """
        fs = PPVC([x[0] for x in self._q_c_input],
                  [x[1] for x in self._q_c_input],
                  self._sample_size)
        return fs

    def summary(self) -> str:
        """Returns a better formatted summary string for the sieve."""
        string = f"PPVC [sampling={self._sample_size}"
        string += f"] -> {self.nfeatures()}:"
        for x in self._q_c_input:
            string += f"\n    > {x[0]} | {x[1]}"
        return string

    def __str__(self) -> str:
        string = "PPVC(" + \
                f"quantile={[x[0] for x in self._q_c_input]}, " + \
                f"constant={[x[1] for x in self._q_c_input]}, " + \
                f"sample_size={self._sample_size}, " + \
                f"segments={self._segments})"
        return string
