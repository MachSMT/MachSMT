from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor,AdaBoostClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler,PolynomialFeatures
from sklearn.neural_network import MLPRegressor
from ..parser import args as settings

def mk_model(n_samples,classifier=False):
    n = min(settings.pca, n_samples)
    n2 = min(settings.pca, n_samples)
    if n > 5:
        return make_pipeline(
                StandardScaler(),
                PCA(n_components=n),
                PolynomialFeatures(degree=2),
                PCA(n_components=n),
                (AdaBoostRegressor() if not classifier else AdaBoostClassifier())
        )
    else:
        return make_pipeline(
                StandardScaler(),
                (AdaBoostRegressor() if not classifier else AdaBoostClassifier())
        )