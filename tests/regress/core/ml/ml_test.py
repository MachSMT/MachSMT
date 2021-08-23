from machsmt.ml.portfolio.portfolio import PortfolioRegressor
from machsmt.ml.model_maker import mk_regressor
import unittest
import os
from sklearn import datasets
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.neural_network import MLPRegressor
from machsmt.ml import Regressor


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
    def test_boston_1(self):
        X, y = datasets.load_boston(return_X_y=True)
        lm = Regressor(pca=False)
        y_ = lm.eval(X, y)
        r2 = Regressor.metrics(y, y_)['r2_score']
        lm.train(X, y)
        lm.predict(X)
        self.assertGreater(r2, 0.6)

    def test_boston_2(self):
        X, y = datasets.load_boston(return_X_y=True)
        lm = Regressor(algo=Ridge, pca=False)
        y_ = lm.eval(X, y)
        r2 = Regressor.metrics(y, y_)['r2_score']
        lm.train(X, y)
        lm.predict(X)
        self.assertGreater(r2, 0.6)

    def test_boston_3(self):
        X, y = datasets.load_boston(return_X_y=True)
        lm = Regressor(algo=LinearRegression, pca=False)
        y_ = lm.eval(X, y)
        r2 = Regressor.metrics(y, y_)['r2_score']
        lm.train(X, y)
        lm.predict(X)
        self.assertGreater(r2, 0.6)

    def test_boston_4(self):
        X, y = datasets.load_boston(return_X_y=True)
        lm = Regressor(algo=MLPRegressor, kwargs=dnn_args, pca=False)
        y_ = lm.eval(X, y)
        r2 = Regressor.metrics(y, y_)['r2_score']
        lm.train(X, y)
        lm.predict(X)
        self.assertGreater(r2, 0.6)


class PortfolioTest(unittest.TestCase):
    def test_1(self):
        X, y = datasets.load_boston(return_X_y=True)

        reg = PortfolioRegressor()
        reg.add_regressor('default', Regressor(pca=False))
        reg.add_regressor('ridge', Regressor(algo=Ridge, pca=False))
        reg.add_regressor('linear', Regressor(algo=LinearRegression, pca=False))
        reg.add_regressor('dnn', Regressor(algo=MLPRegressor, kwargs=dnn_args, pca=False))
        reg.eval(X, y)
        reg.train(X, y)
        reg.predict(X)


class MkRegressorTest(unittest.TestCase):
    def test_1(self):
        X, y = datasets.load_boston(return_X_y=True)

        lm = mk_regressor()
        lm.train(X, y)
        lm.predict(X)


if __name__ == '__main__':
    unittest.main()
