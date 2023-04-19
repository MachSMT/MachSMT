from sklearn.preprocessing import RobustScaler, PolynomialFeatures
from sklearn.multioutput import MultiOutputRegressor
import xgboost
from sklearn.pipeline import make_pipeline

def mk_xgboost_classifier(use_gpu=False):
    return make_pipeline(
        RobustScaler(),
        xgboost.XGBClassifier(),
    )
    
def mk_xgboost_regressor(use_gpu=False):
    if use_gpu:
        return make_pipeline(
            RobustScaler(),
            MultiOutputRegressor(xgboost.XGBRegressor(tree_method='gpu_hist'))
        )
    else:
        return make_pipeline(
            RobustScaler(),
            MultiOutputRegressor(xgboost.XGBRegressor())
        )
