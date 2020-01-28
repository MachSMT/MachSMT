from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

def model_maker(n_points):
    n = min(30,n_points//2)
    return make_pipeline(
            StandardScaler(),
            PCA(n_components=n),
            AdaBoostRegressor()
            # MLPRegressor(hidden_layer_sizes=(10,10,10,5,5,5), activation='relu', solver='adam', learning_rate='adaptive', max_iter=10000, shuffle=True, early_stopping=False, n_iter_no_change=1000)
    )