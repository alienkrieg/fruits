import numpy as np

import fruits

X_1 = np.array([
    [[-4, 0.8, 0, 5, -3], [2, 1, 0, 0, -7]],
    [[5, 8, 2, 6, 0], [-5, -1, -4, -0.5, -8]]
])


def test_increments():
    X_1_1 = fruits.preparation.INC(True).fit_transform(X_1)
    increments = fruits.preparation.INC(zero_padding=False)
    X_1_2 = increments.fit_transform(X_1)

    np.testing.assert_allclose(np.array([
        [[0, 4.8, -0.8, 5, -8], [0, -1, -1, 0, -7]],
        [[0, 3, -6, 4, -6], [0, 4, -3, 3.5, -7.5]]
    ]), X_1_1)
    np.testing.assert_allclose(np.array([
        [[-4, 4.8, -0.8, 5, -8], [2, -1, -1, 0, -7]],
        [[5, 3, -6, 4, -6], [-5, 4, -3, 3.5, -7.5]]
    ]), X_1_2)

    X_1_2_copy = increments.copy().fit_transform(X_1)

    np.testing.assert_allclose(X_1_2, X_1_2_copy)


def test_standardization():
    X_1_1 = fruits.preparation.STD().fit_transform(X_1)

    np.testing.assert_almost_equal(0, np.mean(X_1_1.flatten()))
    np.testing.assert_almost_equal(1, np.std(X_1_1.flatten()))


def test_mav():
    result = fruits.preparation.MAV(2).fit_transform(X_1)

    np.testing.assert_allclose(np.array([
        [[-4, -1.6, 0.4, 2.5, 1], [2, 1.5, 0.5, 0, -3.5]],
        [[5, 6.5, 5, 4, 3], [-5, -3, -2.5, -2.25, -4.25]]
    ]), result)

    result = fruits.preparation.MAV(0.6).fit_transform(X_1)

    np.testing.assert_allclose(np.array([
        [[-12, 2.4, -3.2, 5.8, 2], [6, 3, 3, 1, -7]],
        [[15, 24, 15, 16, 8], [-15, -3, -10, -5.5, -12.5]]
    ]) / 3, result)
