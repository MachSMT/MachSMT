from .regressor import Regressor
from .portfolio import PortfolioRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.neural_network import MLPRegressor


def mk_regressor():
    regressors = {
        'adaboost': Regressor(),
        'ridge': Regressor(algo=Ridge, pca=False),
        'ridge-pca': Regressor(algo=Ridge, pca=True),
    }
    ret = PortfolioRegressor()
    for reg in regressors:
        ret.add_regressor(reg, regressors[reg])
    return ret
