"""Small python module for the creation and manipulation of artificial
time series data.

Available datasets are collected in the ``available_datasets`` list.
"""

import numpy as np

def _multisine(x, coeff):
    return sum([coeff[i, 0]*np.sin(coeff[i, 1]*x+coeff[i, 2])
                for i in range(3)])

def multisine(train_size: int = 100,
              test_size: int = 1000,
              length: int = 100,
              n_classes: int = 2,
              used_sines: int = 3,
              coefficients: list = None) -> tuple:
    """Generates a time series dataset based on a linear concatenation
    of sine functions with random parameters for period length and more.
    These concatenations are the models for each class and a single
    sample is generated by adding a normally distributed error to the
    time series.

    :param train_size: Number of training examples. Each class has
        approximately the same number of examples., defaults to 100
    :type train_size: int, optional
    :param test_size: Number of testing examples. Each class has
        approximately the same number of examples., defaults to 1000
    :type test_size: int, optional
    :param n_classes: Number of classes to generate., defaults to 2
    :type n_classes: int, optional
    :param length: Length of each time series., defaults to 100
    :type length: int, optional
    :param used_sines: Number of sine functions with random parameters
        used for the generation of the dataset., defaults to 5
    :type used_sines: int, optional
    :param coefficients: The coefficients of the sine functions. A numpy
        array of shape ``(n_classes, used_sines, 3)``.
        Only use this option if you already know how these coefficients
        are used. If set to None, random coefficients are used.,
        defaults to None
    :type coefficients: np.ndarray, optional
    :returns: Tuple for the dataset
        ``(X_train, y_train, X_test, y_test)``.
    :rtype: tuple of np.ndarray objects
    """
    train_size_per_class = train_size // n_classes
    train_sizes = [train_size_per_class for i in range(n_classes)]
    remain = train_size - train_size_per_class * n_classes
    while remain > 0:
        train_sizes[remain%n_classes] += 1
        remain -= 1

    test_size_per_class = test_size // n_classes
    test_sizes = [test_size_per_class for i in range(n_classes)]
    remain = test_size - test_size_per_class * n_classes
    while remain > 0:
        test_sizes[remain%n_classes] += 1
        remain -= 1

    x_range = np.linspace(0, 2*np.pi, num=length)
    rand_coeff = 2*np.random.rand(n_classes, used_sines, 3)

    models = [np.vectorize(lambda x: _multisine(x, rand_coeff[i]))(x_range) 
              for i in range(n_classes)]

    X_train = np.zeros((train_size, length))
    X_test = np.zeros((test_size, length))
    y_train = np.zeros(train_size)
    y_test = np.zeros(test_size)

    s = 0
    for i, n_i in enumerate(train_sizes):
        for j in range(n_i):
            X_train[s+j, :] = models[i]
            X_train[s+j, :] += np.random.normal(loc=0, scale=0.5, size=length)
            y_train[s+j] = i
        s += n_i

    s = 0
    for i, n_i in enumerate(test_sizes):
        for j in range(n_i):
            X_test[s+j, :] = models[i]
            X_test[s+j, :] += np.random.normal(loc=0, scale=0.5, size=length)
            y_test[s+j] = i
        s += n_i
        
    X_train = np.expand_dims(X_train, axis=1)
    X_test = np.expand_dims(X_test, axis=1)

    return X_train, y_train, X_test, y_test

def load_dataset(path: str) -> tuple:
    """Returns a time series dataset that is formatted as a .txt file
    and readable with numpy.
    
    :param path: Path to the dataset. The path has to point to a
        folder 'name' with two files:
        'name_TEST.txt' and 'name_TRAIN.txt' where 'name' is the name of
        the dataset.
    :type path: str
    :returns: Tuple (X_train, y_train, X_test, y_test) where X_train
        and X_test are 3-dimensional numpy arrays
    :rtype: tuple
    """
    dataset = path.split("/")[-1]
    train_raw = np.loadtxt(f"{path}/{dataset}_TRAIN.txt")
    test_raw = np.loadtxt(f"{path}/{dataset}_TEST.txt")
    X_train = train_raw[:, 1:]
    y_train = train_raw[:, 0].astype(np.int32)
    X_test = test_raw[:, 1:]
    y_test =  test_raw[:, 0].astype(np.int32)

    X_train = np.expand_dims(X_train, axis=1)
    X_test = np.expand_dims(X_test, axis=1)

    return X_train, y_train, X_test, y_test

def implant_stuttering(X: np.ndarray,
                       stutter_length: float = 0.1) -> np.ndarray:
    """Implants some 'stuttering' to a given array of time series.
    That is, at some indices in each time series a value will be
    repeated consecutively a (random) number of times.
    
    :param X: 3-dim array of multidimensional time series.
    :type X: np.ndarray
    :param stutter_length: Proportional number of time steps each time
        series will be lengthened and where stuttering occurs. This
        value is a float > 0. The actual number of time steps will be
        computed by ``stutter_length * time_series_length``.,
        defaults to 0.1
    :type stutter_length: float, optional
    :returns: Time series array with implanted stuttering.
    :rtype: np.ndarray
    """
    additional_length = int(stutter_length * X.shape[2])
    X_new = np.zeros((X.shape[0],
                      X.shape[1],
                      X.shape[2] + additional_length))
    X_new[:, :, :X.shape[2]] = X[:, :, :]
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            # length already added to the time series
            lengthened = 0
            # index of last value created for stuttering
            prop_index = 0
            while lengthened < additional_length:
                # if X.shape[2] <= prop_index < X.shape[2] + additional_length:
                #     X_new[i, j, prop_index:] = X[i, j, -1]
                #     break
                # choose index and length of stuttering randomly
                stlength = np.random.randint(1, additional_length-lengthened+1)
                stindex = np.random.randint(prop_index + 1,
                                            X.shape[2] + additional_length)
                # if stindex is at last value of X
                if stindex >= (X.shape[2]+lengthened-1):
                    X_new[i, j, X.shape[2]+lengthened-1:] = X[i, j, -1]
                    break
                # shift values where stuttering will be implanted
                start = stindex + 1
                length = X.shape[2] - (start-lengthened)
                to = stindex + stlength + 1
                X_new[i, j, to:to+length] = X_new[i, j, start:start+length]
                # implant stuttering
                X_new[i, j, stindex+1:stindex+stlength+1] = \
                    X_new[i, j, stindex]
                lengthened += stlength
                prop_index = stindex+stlength
    return X_new

def lengthen(X: np.ndarray,
             length: int = 0.1) -> np.ndarray:
    """Lengthens each time series in the given array.
    
    :param X: 3-dim array of multidimensional time series.
    :type X: np.ndarray
    :param length: Proportional length that will be added to each time
        series as a float > 0., defaults to 0.1
    :type length: float, optional
    :returns: Array with lengthened time series.
    :rtype: np.ndarray
    """
    additional_length = int(length * X.shape[2])
    X_new = np.zeros((X.shape[0],
                      X.shape[1],
                      X.shape[2] + additional_length))
    X_new[:, :, :X.shape[2]] = X
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            X_new[i, j, X.shape[2]:] = X[i, j, -1]
    return X_new
