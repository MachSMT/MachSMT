from sklearn.preprocessing import RobustScaler, PolynomialFeatures
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from ..util import warning, die

TORCH_AVAILABLE = False
try:
    import torch
    from .mlp import TabularMLPRegressor, TabularMLPClassifier
    TORCH_AVAILABLE = True
except ImportError as ex:
    warning("PyTorch not available. Please ensure CPU based model")
except OSError as ex:
    assert "cannot open shared object file" in str(ex)
    warning(ex)

def mk_torch_classifier(use_gpu=False):
    if TORCH_AVAILABLE and use_gpu and torch.cuda.is_available():
        return make_pipeline(
            RobustScaler(),
            TabularMLPClassifier()
        )
    else:
        raise ValueError
    
def mk_torch_regressor(use_gpu=False):
    if TORCH_AVAILABLE and use_gpu and torch.cuda.is_available():
        return make_pipeline(
            RobustScaler(),
            TabularMLPRegressor()
        )
    else:
        raise ValueError
