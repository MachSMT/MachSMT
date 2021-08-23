from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.decomposition import PCA
from sklearn import metrics
from sklearn.pipeline import make_pipeline

import numpy as np

from ...config import config


class Regressor:
    def __init__(
        self,
        scale=True,
        pca=True,
        n_pca=config.pca,
        algo=AdaBoostRegressor,
        args=[],
        kwargs={},
        # X=[],
        # Y=[],
    ) -> None:
        self.scale = scale
        self.algo = algo
        self.algo_args = args
        self.algo_kwargs = kwargs
        self.pca = pca
        self.n_pca = n_pca
        self.lm = self.mk_model()

    def mk_model(self, use_pca=True):
        args = []
        if self.scale:
            args.append(StandardScaler())
        if self.pca and use_pca:
            args.append(PCA(n_components=self.n_pca))
        args.append(self.algo(*self.algo_args, **self.algo_kwargs))
        return make_pipeline(*args)

    @staticmethod
    def metrics(Y, Y_):
        return {
            'explained_variance_score': metrics.explained_variance_score(Y, Y_),
            'max_error': metrics.max_error(Y, Y_),
            'mean_absolute_error': metrics.mean_absolute_error(Y, Y_),
            'mean_squared_error': metrics.mean_squared_error(Y, Y_),
            'mean_squared_log_error': metrics.mean_squared_log_error(np.abs(Y), np.abs(Y_)),
            'median_absolute_error': metrics.median_absolute_error(Y, Y_),
            'r2_score': metrics.r2_score(Y, Y_),
            'mean_poisson_deviance': metrics.mean_poisson_deviance(np.abs(Y), np.abs(Y_)),
            'mean_gamma_deviance': metrics.mean_gamma_deviance(np.abs(Y), np.abs(Y_)),
            'mean_absolute_percentage_error': metrics.mean_absolute_percentage_error(np.abs(Y), np.abs(Y_)),
        }

    def eval(self, X, Y, k=config.k):
        k_fold_args = {'n_splits': k, 'shuffle': True, 'random_state': config.rng}
        Y_out = Y.copy()
        stats = {}
        X, Y = np.array(X), np.array(Y)
        for train, test in KFold(**k_fold_args).split(X):
            self.train(X[train], Y[train])
            y_ = self.predict(X[test])
            for it, indx in enumerate(test):
                Y_out[indx] = y_[it]
        return Y_out

    def train(self, X, Y):
        n_samples, n_features = X.shape
        use_pca = min(n_samples, n_features) > self.n_pca
        self.lm = self.mk_model(use_pca=use_pca)
        self.lm.fit(X, Y.ravel())

    def predict(self, X):
        return self.lm.predict(X)
