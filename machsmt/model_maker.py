from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

def mk_regressor(n_samples,n_features):
    n = min(10, n_samples, n_features)
    if n > 5:
        return make_pipeline(
                StandardScaler(),
                PCA(n_components=n),
                AdaBoostRegressor()
        )
    else:
        return make_pipeline(
                StandardScaler(),
                AdaBoostRegressor()
        )