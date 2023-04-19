
from .mach_scikit  import mk_scikit_classifier, mk_scikit_regressor
from ..ex import MachSMT_GPU_Not_Available
GPU_AVAILABLE = True
try:
    from .mach_torch   import mk_torch_classifier, mk_torch_regressor
except ImportError as ex:
    GPU_AVAILABLE = False
    # warning printed previously

from .mach_xgboost import mk_xgboost_classifier, mk_xgboost_regressor
from ..config import args


def mk_classifier(core=None):
    if core is None:
        core = args.ml_core
    if core == 'scikit':
        return mk_scikit_classifier()
    elif core == "torch":
        if not GPU_AVAILABLE:
            raise MachSMT_GPU_Not_Available
        return mk_torch_classifier()
    elif core == 'xgboost':
        return mk_xgboost_classifier()
    else: raise NotImplementedError

def mk_regressor(core=None):
    if core is None:
        core = args.ml_core
    if core == 'scikit':
        return mk_scikit_regressor()
    elif core == "torch":
        if not GPU_AVAILABLE:
            raise MachSMT_GPU_Not_Available
        return mk_torch_regressor()
    elif core == 'xgboost':
        return mk_xgboost_regressor()
    else: raise NotImplementedError
    