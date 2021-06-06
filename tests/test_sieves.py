import pytest
import numpy as np

import fruits

X_1 = np.array([
                [[-4,0.8,0,5,-3], [2,1,0,0,-7]],
                [[5,8,2,6,0], [-5,-1,-4,-0.5,-8]]
               ])

def test_ppv():
    ppv_1 = fruits.features.PPV(quantile=0, constant=True)
    ppv_2 = fruits.features.PPV(quantile=0.5, constant=False,
                                sample_size=1)

    np.testing.assert_allclose(np.array([3/5,4/5]), ppv_1.fit_sieve(X_1[0]))
    np.testing.assert_allclose(np.array([1,0]), ppv_2.fit_sieve(X_1[1]))

    ppv_1_copy = ppv_1.copy()

    np.testing.assert_allclose(ppv_1.fit_sieve(X_1[0]),
                               ppv_1_copy.fit_sieve(X_1[0]))

    ppvc_1 = fruits.features.PPVC(quantile=0, constant=True)

    np.testing.assert_allclose([0.4,0.4], ppvc_1.fit_sieve(X_1[0]))

    with pytest.raises(ValueError):
        fruits.features.PPV(quantile=[0.5,0.1,0], constant=[False,True,False])

    ppv_group_1 = fruits.features.PPV(quantile=[0.5,0.1,0.7],
                                      constant=False,
                                      sample_size=1,
                                      segments=False)

    np.testing.assert_allclose(np.array([[1,1,3/5],[0,4/5,0]]),
                               ppv_group_1.fit_sieve(X_1[1]))

    ppv_group_2 = fruits.features.PPV(quantile=[0.5,0.1,0.7],
                                      constant=False,
                                      sample_size=1,
                                      segments=True)

    np.testing.assert_allclose(np.array([[0,2/5],[4/5,0]]),
                               ppv_group_2.fit_sieve(X_1[1]))

    ppv_group_3 = fruits.features.PPV(quantile=[-5,0,2],
                                      constant=True,
                                      sample_size=1,
                                      segments=False)

    np.testing.assert_allclose(np.array([[1,1,4/5],[4/5,0,0]]),
                               ppv_group_3.fit_sieve(X_1[1]))

    ppv_group_4 = fruits.features.PPV(quantile=[0,-5,2],
                                      constant=True,
                                      sample_size=1,
                                      segments=True)

    np.testing.assert_allclose(np.array([[0,1/5],[4/5,0]]),
                               ppv_group_4.fit_sieve(X_1[1]))

    ppv_group_4_copy = ppv_group_4.copy()

    np.testing.assert_allclose(ppv_group_4.fit_sieve(X_1[1]),
                               ppv_group_4_copy.fit_sieve(X_1[1]))

def test_min_max():
    max_ = fruits.features.MAX()
    min_ = fruits.features.MIN()

    np.testing.assert_allclose(np.array([5,2]), max_.fit_sieve(X_1[0]))
    np.testing.assert_allclose(np.array([0,-8]), min_.fit_sieve(X_1[1]))

    max_cut_1 = fruits.features.MAX(cut=3)
    max_cut_2 = fruits.features.MAX(cut=0.5)

    np.testing.assert_allclose(np.array([0.8,2]), max_cut_1.fit_sieve(X_1[0]))
    np.testing.assert_allclose(np.array([0.8,2]), max_cut_2.fit_sieve(X_1[0]))

    min_cut_1 = fruits.features.MIN(cut=3)
    min_cut_2 = fruits.features.MIN(cut=0.5)

    np.testing.assert_allclose(np.array([-4,0]), min_cut_1.fit_sieve(X_1[0]))
    np.testing.assert_allclose(np.array([5,-5]), min_cut_2.fit_sieve(X_1[1]))

    max_cut_group_1 = fruits.features.MAX(cut=[-1, 3, 1],
                                          segments=False)

    np.testing.assert_allclose(np.array([[5,0.8,-4],[2,2,2]]),
                               max_cut_group_1.fit_sieve(X_1[0]))

    min_cut_group_1 = fruits.features.MIN(cut=[-1, 3, 1],
                                          segments=False)

    np.testing.assert_allclose(np.array([[0,2,5],[-8,-5,-5]]),
                               min_cut_group_1.fit_sieve(X_1[1]))

    max_cut_group_2 = fruits.features.MAX(cut=[-1, 0.2, 0.7, 0.5],
                                          segments=True)

    np.testing.assert_allclose(np.array([[0.8,5,5],[0,0,0]]),
                               max_cut_group_2.fit_sieve(X_1[0]))

    min_cut_group_2 = fruits.features.MIN(cut=[-1, 0.2, 0.7, 0.5],
                                          segments=True)

    np.testing.assert_allclose(np.array([[-4,0,-3],[0,0,-7]]),
                               min_cut_group_2.fit_sieve(X_1[0]))

    max_cut_group_2_copy = max_cut_group_2.copy()

    np.testing.assert_allclose(max_cut_group_2.fit_sieve(X_1[0]),
                               max_cut_group_2_copy.fit_sieve(X_1[0]))

    min_cut_group_2_copy = min_cut_group_2.copy()

    np.testing.assert_allclose(min_cut_group_2.fit_sieve(X_1[0]),
                               min_cut_group_2_copy.fit_sieve(X_1[0]))

def test_end():
    end = fruits.features.END()

    np.testing.assert_allclose(np.array([-3,-7]), end.fit_sieve(X_1[0]))

    end_cut = fruits.features.END(cut=0.2)

    np.testing.assert_allclose(np.array([-4,0]), end_cut.fit_sieve(X_1[0]))

    end_cut_group = fruits.features.END(cut=[1, 0.2, 0.8, 4, -1])

    np.testing.assert_allclose(np.array([[-4,-4,5,5,-3],[2,0,0,0,-7]]),
                               end_cut_group.fit_sieve(X_1[0]))

    end_cut_group_copy = end_cut_group.copy()

    np.testing.assert_allclose(end_cut_group.fit_sieve(X_1[0]),
                               end_cut_group_copy.fit_sieve(X_1[0]))
