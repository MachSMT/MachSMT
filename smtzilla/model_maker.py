from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

def model_maker(pca=True):
    # pca = False
    if pca:
        return make_pipeline(
            StandardScaler(),
            PCA(n_components=10),
            AdaBoostRegressor()
            #MLPRegressor(hidden_layer_sizes=(100,100,50,50,10,10,10,5,5,5), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, power_t=0.5, max_iter=20000000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=100)
        )
    else:
        return make_pipeline(
            StandardScaler(),
            AdaBoostRegressor()
            #MLPRegressor(hidden_layer_sizes=(100,100,50,50,10,10,10,5,5,5), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, power_t=0.5, max_iter=20000000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=100)
        )