import numpy as np

import fruits

X_1 = np.array([
                [[-4,0.8,0,5,-3], [2,1,0,0,-7]],
                [[5,8,2,6,0], [-5,-1,-4,-0.5,-8]]
               ])

def test_ppv():
    const_ppv = fruits.features.PPV(quantile=0, constant=True)
    ppv_1 = const_ppv.fit_sieve(X_1[0])
    ppv_2 = fruits.features.PPV(quantile=0.5, constant=False,
                                sample_size=1).fit_sieve(X_1[1])

    np.testing.assert_allclose(np.array([3/5,4/5]), ppv_1)
    np.testing.assert_allclose(np.array([1,0]), ppv_2)

    ppv_1_copy = const_ppv.copy().fit_sieve(X_1[0])

    np.testing.assert_allclose(ppv_1, ppv_1_copy)

    ppv_c = fruits.features.PPVC(quantile=0, constant=True)

    np.testing.assert_allclose([0.4,0.4], ppv_c.fit_sieve(X_1[0]))

def test_min_max():
    maxi = fruits.features.MAX().fit_sieve(X_1[0])
    mini = fruits.features.MIN().fit_sieve(X_1[1])

    np.testing.assert_allclose(np.array([5,2]), maxi)
    np.testing.assert_allclose(np.array([0,-8]), mini)
