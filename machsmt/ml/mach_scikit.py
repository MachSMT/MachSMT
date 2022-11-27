from sklearn.preprocessing import RobustScaler, PolynomialFeatures
from sklearn.ensemble import AdaBoostRegressor, AdaBoostClassifier
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline

def mk_scikit_classifier():
    return make_pipeline(
        RobustScaler(),
        AdaBoostClassifier()
    )
    
def mk_scikit_regressor():
    return make_pipeline(
        RobustScaler(),
        MultiOutputRegressor(AdaBoostRegressor()),
    )
