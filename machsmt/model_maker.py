from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

def mk_regressor():
    return make_pipeline(
            StandardScaler(),
            PCA(n_components=5),
            AdaBoostRegressor()
    )