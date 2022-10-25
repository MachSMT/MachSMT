from numpy import e
from sklearn.linear_model import RidgeCV
from sklearn.svm import SVR
from sklearn.preprocessing import RobustScaler
from ...config import config
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import AdaBoostRegressor
from sklearn.decomposition import PCA
from sklearn.multioutput import MultiOutputRegressor
from ...config import config
import numpy as np

class StackRegressor:
    def __init__(self, lm='ridge'):
        if lm == 'ridge':
            self.lm = make_pipeline(
                RobustScaler(),
                RidgeCV(),
            )
        elif lm == 'ada':
            self.lm = make_pipeline(
                RobustScaler(),
                MultiOutputRegressor(AdaBoostRegressor()),
            )
    def train(self, X, Y):
        assert len(X) == len(Y)
        self.lm.fit(X,Y)
        
    fit = train
    
    def predict(self, X):
        return self.lm.predict(X)