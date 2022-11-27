from sklearn.preprocessing import RobustScaler, PolynomialFeatures
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from .mlp import TabularMLPRegressor, TabularMLPClassifier
from ..util import warning, die
import torch
def mk_torch_classifier():
    if torch.cuda.is_available():
        return make_pipeline(
            RobustScaler(),
            TabularMLPClassifier()
        )
    else:
        warning("GPU Not available. Using CPU")
        return make_pipeline(
            RobustScaler(),
            TabularMLPClassifier(train_device='cpu')
        )
    
def mk_torch_regressor():
    if torch.cuda.is_available():
        return make_pipeline(
            RobustScaler(),
            TabularMLPRegressor()
        )
    else:
        warning("GPU Not available. Using CPU")
        return make_pipeline(
            RobustScaler(),
            TabularMLPRegressor(train_device='cpu')
        )
