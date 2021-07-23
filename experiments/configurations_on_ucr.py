"""This python module contains a class ClassificationPipeline, that
is able to perform a classification task for time series data from
timeseriesclassification.com.

The datasets should be available in a .txt file and readable with
numpy.

A ClassificationPipeline object can be used via import in another
python script or in a terminal/console by using this file as an
executable script.

Usage:
    $ python configurations_on_ucr.py -d [directory of datasets]

Optional arguments:
    -u : Path to a txt file with names of datasets. Only these datasets
         will then be loaded from the dataset directory.
    -o : Output file path.,
         defaults to "./ucr_configuration_results.txt"
    -r : File with the accuracy results from rocket.,
         defaults to "./rocket_results_ucr.csv"

The fruits configurations to use for feature calculation are defined
in the file configurations.py which should be located in the same
directory as this file.
"""

import os
import time
import logging
import argparse
from timeit import default_timer as Timer

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeClassifierCV
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from configurations import CONFIGURATIONS
import tsdata

class ClassificationPipeline:
    """Class that manages a time series classification with fruits and a
    classifier from sklearn.
    The classification results will be compared with those from ROCKET.
    The results will be flushed in real-time to an output file.

    :param output_file: Path of the file to write the log to. If the
        file already exists, a time stamp will be added to the new file
        name.
    :type output_file: str
    :param rocket_results: String of the path to a csv file with
        the classification results from ROCKET.
    :type rocket_results: str
    :param verbose: If `True`, print status of classfication to the
        console., defaults to `True`
    :type verbose: bool, optional
    :param classifier: Classifier with fit and score method from
        sklearn., defaults to
        ``RidgeClassifierCV(alphas=np.logspace(-3,3,10),
                            normalize=True)``
    :type classfier: ClassifierMixin from sklearn, optional
    :param scaler: An object that allows calls of fit() and transform()
        and that scales the features extracted by the fruits pipeline.,
        defaults to an identity scaler (that doesn't transform at all)
    :type scaler: Some scaler, preferably from sklearn., optional
    """
    table_header = "{:=^30}{:=^20}{:=^25}{:=^25}{:=^25}{:=^3}".format(
                        "Dataset",
                        "Train/Test/Length",
                        "Feature Calculation Time",
                        "FRUITS Accuracy",
                        "ROCKET Mean Accuracy",
                        "M",
                    )

    def __init__(self,
                 output_file: str,
                 rocket_results: str,
                 verbose: bool = True,
                 classifier=None,
                 scaler=None,
                 comet_experiment=None):
        self._results = None
        self._verbose = verbose
        self._datasets = []
        self._paths = []
        self._rocket_csv = pd.read_csv(rocket_results)
        self._output_file = output_file
        self._comet_exp = comet_experiment
        if classifier is None:
            self._classifier = RidgeClassifierCV(
                                    alphas=np.logspace(-3,3,10),
                                    normalize=True)
        else:
            self._classifier = classifier
        if scaler is None:
            self._scaler = FunctionTransformer(lambda X: X, validate=False)
        else:
            self._scaler = scaler

    def _set_up_logger(self):
        # add timestamp to output file if it exists already
        if os.path.isfile(self._output_file):
            self._output_file = self._output_file.split(".")
            self._output_file[-2] += "-"+time.strftime("%Y-%m-%d-%H%M%S")
            self._output_file = ".".join(self._output_file)
        # empty the output file if it exists already
        with open(self._output_file, "w") as f:
            f.truncate(0)
        # create a logger that flushes accuracy results to the given
        # file path at the end of the classification of each dataset
        self.logger = logging.Logger("fruits classification results")
        fh = logging.FileHandler(self._output_file)
        self.logger.addHandler(fh)

    def append_data(self, path: str, use_only: list = None):
        """Finds time series datasets in the specified directory for
        later usage.
        
        :param path: Path of a directory that contains folders
            structured like the datasets you get from
            timeseriesclassification.com.
        :type path: str
        :param use_only: List of dataset names. Only the datasets in
            this list will be remembered. If `None`, then all datasets
            are used., defaults to None
        :type use_only: list of strings
        """
        if not path.endswith("/"):
            path += "/"
        self._paths.append(path)
        self._datasets.append([])
        for folder in sorted(os.listdir(path)):
            if os.path.isdir(path + folder):
                if use_only is None or folder in use_only:
                    self._datasets[-1].append(folder)

    def classify(self, fruits_configurations: list, log_fruit: bool = False):
        """Classifies all datasets specified earlier.

        :param fruits_configurations: A list of fruits configurations to
            use for classification.
        :type fruits_configurations: list of fruits.Fruit objects
        """
        self._set_up_logger()
        n_datasets = sum([len(ds) for ds in self._datasets])
        results = np.zeros((len(fruits_configurations), n_datasets, 4))

        for k, fruit in enumerate(fruits_configurations):

            self.logger.info(f"Configuration: {fruit.name}, " +
                             f"Features: {fruit.nfeatures()}\n")
            self.logger.info(self.table_header)

            if self._verbose:
                print(f"Starting: Configuration {k+1}")

            i = 0

            for j, path in enumerate(self._paths):

                for dataset in self._datasets[j]:

                    if self._comet_exp is not None:
                        self._comet_exp.log_dataset_info(name=dataset)
                        self._comet_exp.set_step(i)

                    X_train, y_train, X_test, y_test = tsdata.load_dataset(
                        path+dataset)

                    if self._comet_exp is not None:
                        with self._comet_exp.train():
                            start = Timer()
                            fruit.fit(X_train)
                            X_train_feat = fruit.transform(X_train)
                            end_train = Timer() - start
                            self._scaler.fit(X_train_feat)
                            X_train_feat_scaled = self._scaler.transform(
                                                    X_train_feat)
                            self._classifier.fit(X_train_feat_scaled, y_train)

                        with self._comet_exp.test():
                            start = Timer()
                            X_test_feat = fruit.transform(X_test)
                            end_test = Timer() - start
                            X_test_feat_scaled = self._scaler.transform(
                                                    X_test_feat)

                            results[k, i, 1] = self._classifier.score(
                                                    X_test_feat_scaled, y_test)
                            self._comet_exp.log_metric("accuracy",
                                                       results[k,i,1])
                    else:
                        start = Timer()
                        fruit.fit(X_train)
                        X_train_feat = fruit.transform(X_train)
                        X_test_feat = fruit.transform(X_test)
                        results[k, i, 0] = Timer() - start

                        self._scaler.fit(X_train_feat)
                        X_train_feat_scaled = self._scaler.transform(
                                                        X_train_feat)
                        X_test_feat_scaled = self._scaler.transform(
                                                        X_test_feat)

                        self._classifier.fit(X_train_feat_scaled, y_train)

                        results[k, i, 1] = self._classifier.score(
                                                    X_test_feat_scaled, y_test)


                    results[k, i, 0] = end_train + end_test
                    mark = " "
                    rocket_acc = self._rocket_csv[
                        self._rocket_csv["dataset"] == dataset][
                            "accuracy_mean"].to_numpy()[0]
                    fruits_acc = results[k, i, 1]
                    if fruits_acc >= rocket_acc:
                        mark = "X"
                    self.logger.info(("{: ^30}{: ^20}{: ^25}{: ^25}" +
                                      "{: ^25}{: ^3}").format(
                        dataset,
                        f"{X_train.shape[0]}/{X_test.shape[0]}/" + \
                        f"{X_train.shape[2]}",
                        round(results[k, i, 0], 3),
                        round(fruits_acc, 3),
                        round(rocket_acc, 3),
                        mark))
                    self.logger.handlers[0].flush()
                    if self._verbose:
                        print(".", end="", flush=True)

                    i += 1

            self.logger.info(len(self.table_header) * "-")
            mark = " "
            mean_rocket_a = self._rocket_csv["accuracy_mean"].to_numpy().mean()
            mean_fruits_a = results[k, :, 1].mean()
            if mean_fruits_a >= mean_rocket_a:
                mark = "+++"
            self.logger.info(("{: ^30}{: ^20}{: ^25}{: ^25}{: ^25}" +
                              "{: ^3}").format(
                                "MEAN",
                                "-/-/-",
                                round(results[k, :, 0].mean(), 6),
                                round(results[k, :, 1].mean(), 6),
                                round(mean_rocket_a, 6),
                                mark))
            if log_fruit:
                self.logger.info("\n"+fruit.summary())

            if k < len(fruits_configurations)-1:
                self.logger.info("\n" + len(self.table_header)*"*" + "\n")

            if self._verbose:
                print(f"\nDone.")


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--dataset_path", type=str, required=True)
    parser.add_argument("-u", "--use_datasets", default=None)
    parser.add_argument("-o", "--output_file",
                        default="./ucr_configuration_results.txt")
    parser.add_argument("-r", "--rocket_results",
                        default="./rocket_results_ucr.csv")

    arguments = parser.parse_args()

    use_sets = None
    if arguments.use_datasets is not None:
        with open(arguments.use_datasets) as f:
            use_sets = f.read().split("\n")
        use_sets.remove("")

    pipeline = ClassificationPipeline(arguments.output_file,
                                      arguments.rocket_results,
                                      scaler=StandardScaler())
    pipeline.append_data(arguments.dataset_path, use_sets)
    pipeline.classify(CONFIGURATIONS)
