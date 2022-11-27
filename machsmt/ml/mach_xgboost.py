from sklearn.preprocessing import RobustScaler, PolynomialFeatures
from sklearn.multioutput import MultiOutputRegressor
import xgboost
from sklearn.pipeline import make_pipeline

def mk_xgboost_classifier():
    return make_pipeline(
        RobustScaler(),
        xgboost.XGBClassifier(),
    )
    
def mk_xgboost_regressor():
    return make_pipeline(
        RobustScaler(),
        MultiOutputRegressor(xgboost.XGBRegressor())
    )
