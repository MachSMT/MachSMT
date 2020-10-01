from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor,AdaBoostClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler,PolynomialFeatures
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import Ridge, RidgeClassifier
from ..parser import args as settings

hidden_layer_sizes = (100,100,10,10,10)
activation = 'relu'
max_iter = 2 * 10 ** 3
n_iter_no_change = 30

def mk_model(n_samples,classifier=False):
    n = min(n_samples,settings.pca)
    return make_pipeline(
            StandardScaler(),
            PCA(n_components=n),
            (AdaBoostRegressor() if not classifier else AdaBoostClassifier())
    )