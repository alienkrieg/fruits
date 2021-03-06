import numpy as np

import fruits

X_1 = np.array([
    [[-4, 0.8, 0, 5, -3], [2, 1, 0, 0, -7]],
    [[5, 8, 2, 6, 0], [-5, -1, -4, -0.5, -8]]
])


def test_lag():
    L = fruits.preparation.LAG()

    np.testing.assert_allclose(np.array([
        [
            [-4, 0.8, 0.8, 0, 0, 5, 5, -3, -3],
            [-4, -4, 0.8, 0.8, 0, 0, 5, 5, -3],
            [2, 1, 1, 0, 0, 0, 0, -7, -7],
            [2, 2, 1, 1, 0, 0, 0, 0, -7],
        ],
        [
            [5, 8, 8, 2, 2, 6, 6, 0, 0],
            [5, 5, 8, 8, 2, 2, 6, 6, 0],
            [-5, -1, -1, -4, -4, -0.5, -0.5, -8, -8],
            [-5, -5, -1, -1, -4, -4, -0.5, -0.5, -8],
        ],
    ]), L.fit_transform(X_1))


def test_one():
    one = fruits.preparation.ONE()

    np.testing.assert_allclose(np.array([
        [[-4, 0.8, 0, 5, -3],
         [2, 1, 0, 0, -7],
         [1, 1, 1, 1, 1]],
        [[5, 8, 2, 6, 0],
         [-5, -1, -4, -0.5, -8],
         [1, 1, 1, 1, 1]]
    ]), one.fit_transform(X_1))
