from machsmt.ml import mk_classifier, mk_regressor
from machsmt.config import args
from machsmt.ex import MachSMT_GPU_Not_Available
import unittest
import os
import sklearn.datasets as data
from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics
import numpy as np
from scipy.stats import mode


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


dnn_args = {
    'hidden_layer_sizes': (15, 10, ),
    'learning_rate': 'adaptive',
    'max_iter': 5 * 10**3,
    'n_iter_no_change': 1,
}


class RegressorTest(unittest.TestCase):
    def test_scikit(self):
        X,Y = data.make_regression(1000,10,n_targets=3)
        X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.5)
        lm = mk_regressor(core='scikit')
        lm.fit(X_train,Y_train)
        avg = np.zeros(Y_test.shape)
        for it in range(Y.shape[1]): # for every column
            avg[:, it] = np.mean(Y_train[:, it])
        Y_p = lm.predict(X_test)
        self.assertGreater(metrics.r2_score(Y_p, Y_test), metrics.r2_score(avg, Y_test))
        
    def test_xgboost(self):
        X,Y = data.make_regression(1000,10,n_targets=3)
        X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.5)
        lm = mk_regressor(core='xgboost')
        lm.fit(X_train,Y_train)
        avg = np.zeros(Y_test.shape)
        for it in range(Y.shape[1]): # for every column
            avg[:, it] = np.mean(Y_train[:, it])
        Y_p = lm.predict(X_test)
        self.assertGreater(metrics.r2_score(Y_p, Y_test), metrics.r2_score(avg, Y_test))
        
        
    def test_torch(self):
        try:        
            X,Y = data.make_regression(1000,10,n_targets=3)
            X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.5)
            lm = mk_regressor(core='torch')
            lm.fit(X_train,Y_train)
            avg = np.zeros(Y_test.shape)
            for it in range(Y.shape[1]): # for every column
                avg[:, it] = np.mean(Y_train[:, it])
            Y_p = lm.predict(X_test)
            self.assertGreater(metrics.r2_score(Y_p, Y_test), metrics.r2_score(avg, Y_test))
        except MachSMT_GPU_Not_Available:
            pass        
        
class ClassifierTest(unittest.TestCase):
    def test_scikit(self):
        X,Y = data.make_classification(10000,10,n_classes=3, n_clusters_per_class=1)
        X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.5)
        lm = mk_classifier(core='scikit')
        lm.fit(X_train,Y_train)
        mode_class = np.zeros(Y_test.shape) + mode(Y_train).mode[0]
        Y_p = lm.predict(X_test)
        self.assertGreater(metrics.accuracy_score(Y_p, Y_test), metrics.accuracy_score(mode_class, Y_test))
        
    def test_xgboost(self):
        X,Y = data.make_classification(10000,10,n_classes=3, n_clusters_per_class=1)
        X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.5)
        lm = mk_classifier(core='xgboost')
        lm.fit(X_train,Y_train)
        mode_class = np.zeros(Y_test.shape) + mode(Y_train).mode[0]
        Y_p = lm.predict(X_test)
        self.assertGreater(metrics.accuracy_score(Y_p, Y_test), metrics.accuracy_score(mode_class, Y_test))
        
        
    def test_torch(self):
        try:
            X,Y = data.make_classification(10000,10,n_classes=3, n_clusters_per_class=1)
            X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.5)
            lm = mk_classifier(core='torch')
            lm.fit(X_train,Y_train)
            mode_class = np.zeros(Y_test.shape) + mode(Y_train).mode[0]
            Y_p = lm.predict(X_test)
            self.assertGreater(metrics.accuracy_score(Y_p, Y_test), metrics.accuracy_score(mode_class, Y_test))
        except MachSMT_GPU_Not_Available:
            pass
if __name__ == '__main__':
    unittest.main()
