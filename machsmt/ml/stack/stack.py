from numpy import e
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV, SGDRegressor, LassoCV, ElasticNetCV
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, RobustScaler
from ...config import config
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import AdaBoostRegressor
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from ...config import config
import numpy as np

import time , pdb

MAX_ITER = 10

class StackRegressor:
    def __init__(self):
        self.lm = make_pipeline(
            RobustScaler(),
            StackingRegressor(
                estimators=[
                    # ('ridge-10', make_pipeline(PCA(n_components=10), RidgeCV())),
                    # ('ridge-25', make_pipeline(PCA(n_components=25), RidgeCV())),
                    # ('ridge-50', make_pipeline(PCA(n_components=50), RidgeCV())),
                    ('ridge', make_pipeline(RidgeCV())),

                    # ('sgd-10', make_pipeline(PCA(n_components=10), SGDRegressor(max_iter=max_iter))),
                    # ('sgd-25', make_pipeline(PCA(n_components=25), SGDRegressor(max_iter=max_iter))),
                    # ('sgd-50', make_pipeline(PCA(n_components=50), SGDRegressor(max_iter=max_iter))),
                    # ('sgd', make_pipeline(SGDRegressor(max_iter=max_iter))),

                    # ('lasso-10', make_pipeline(PCA(n_components=10), LassoCV(max_iter=max_iter))),
                    # ('lasso-25', make_pipeline(PCA(n_components=25), LassoCV(max_iter=max_iter))),
                    # ('lasso-50', make_pipeline(PCA(n_components=50), LassoCV(max_iter=max_iter))),
                    # ('lasso', make_pipeline(LassoCV(max_iter=max_iter))),

                    # ('elastic-10', make_pipeline(PCA(n_components=10), ElasticNetCV(max_iter=max_iter))),
                    # ('elastic-25', make_pipeline(PCA(n_components=25), ElasticNetCV(max_iter=max_iter))),
                    # ('elastic-50', make_pipeline(PCA(n_components=50), ElasticNetCV(max_iter=max_iter))),
                    # ('elastic', make_pipeline(ElasticNetCV(max_iter=max_iter))),


                    # ('ada-10', make_pipeline(PCA(n_components=10), AdaBoostRegressor())),
                    # ('ada-25', make_pipeline(PCA(n_components=25), AdaBoostRegressor())),
                    # ('ada-50', make_pipeline(PCA(n_components=50), AdaBoostRegressor())),
                    ('ada', make_pipeline(AdaBoostRegressor())),


                    ('dnn', MLPRegressor(hidden_layer_sizes=(1000, 1000, 200, 200, 200, 200), activation='relu', max_iter=MAX_ITER, n_iter_no_change=MAX_ITER, validation_fraction=0, early_stopping=False, tol=0, verbose=True, warm_start=True,learning_rate='constant', learning_rate_init=10**-5))
                ],
                final_estimator=make_pipeline(RobustScaler(), AdaBoostRegressor()),
                verbose=True,
                n_jobs=config.cores,
                cv=config.k,
                passthrough=True,
            )
        )
        # self.lm = make_pipeline(RobustScaler(), AdaBoostRegressor())
        # self.lm = make_pipeline(RobustScaler(), MLPRegressor(hidden_layer_sizes=(1000, 1000, 200, 200, 200, 200), activation='relu', max_iter=MAX_ITER, n_iter_no_change=MAX_ITER, validation_fraction=0, early_stopping=False, tol=0, verbose=True, warm_start=True,learning_rate='constant', learning_rate_init=10**-5))
    def train(self, X, Y):
        mlp = self.lm
        mlp.learning_rate_init = np.random.choice([10 ** -x for x in [5, 6, 7]])
        mlp.batch_size = np.random.choice([32, 64, 128, 256, 512, 1024])
        mlp.max_iter = MAX_ITER
        max_time = 60
        start = time.time()
        while time.time() - start < 60:
            mlp.fit(X,Y)
            mlp.set_params(mlpregressor__batch_size=np.random.choice([32, 64, 128, 256, 512, 1024]))
            mlp.set_params(mlpregressor__learning_rate_init=np.random.choice([10 ** -x for x in [5, 6, 7]]))
        print(f"finished {config.lib}")
    def predict(self, X):
        return self.lm.predict(X)