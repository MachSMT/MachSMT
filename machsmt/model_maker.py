from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor,AdaBoostClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler,PolynomialFeatures
from sklearn.neural_network import MLPRegressor
import machsmt.settings as settings

def mk_model(n_samples,classifier=False):
    n = min(settings.N_PCA_COMPONENTS, n_samples)
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