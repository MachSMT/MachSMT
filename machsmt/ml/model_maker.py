from .regressor import Regressor
from .portfolio import PortfolioRegressor
from sklearn.linear_model import Ridge, LinearRegression, RidgeCV
from sklearn.neural_network import MLPRegressor
from ..util import warning

# try:
from sklearnex import patch_sklearn
patch_sklearn()

def mk_regressor():
    regressors = {
        'ridge-pca5': Regressor(algo=RidgeCV, pca=True, n_pca=5),
        'ridge-pca10': Regressor(algo=RidgeCV, pca=True, n_pca=10),
        'ridge-pca15': Regressor(algo=RidgeCV, pca=True, n_pca=15),
        'ridge-pca25': Regressor(algo=RidgeCV, pca=True, n_pca=20),
        'ridge-pca50': Regressor(algo=RidgeCV, pca=True, n_pca=50),
        'ridge': Regressor(algo=RidgeCV),

        'ada-pca5': Regressor(pca=True, n_pca=5),
        'ada-pca10': Regressor(pca=True, n_pca=10),
        'ada-pca15': Regressor(pca=True, n_pca=15),
        'ada-pca25': Regressor(pca=True, n_pca=20),
        'ada-pca50': Regressor(pca=True, n_pca=50),
        'ada': Regressor(pca=True, n_pca=50),    }
    ret = PortfolioRegressor()
    for reg in regressors:
        ret.add_regressor(reg, regressors[reg])
    return ret