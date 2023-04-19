
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
    # return YOUR_CLASSIFIER_HERE

    # make out of the box classifier
    use_gpu = args.use_gpu
    if core is None:
        core = args.ml_core
    if core == 'scikit':
        return mk_scikit_classifier()
    elif core == "torch":
        if use_gpu and not GPU_AVAILABLE:
            raise MachSMT_GPU_Not_Available
        try:
            return mk_torch_classifier(use_gpu=use_gpu)
        except ValueError as ex:
            raise MachSMT_GPU_Not_Available
    elif core == 'xgboost':
        if use_gpu and not GPU_AVAILABLE:
            raise MachSMT_GPU_Not_Available
        return mk_xgboost_classifier(use_gpu=use_gpu)
    else: raise NotImplementedError

def mk_regressor(core=None):
    # return YOUR_REGRESSOR_HERE

    # make out of the box regressor
    use_gpu = args.use_gpu
    if core is None:
        core = args.ml_core
    if core == 'scikit':
        return mk_scikit_regressor()
    elif core == "torch":
        if use_gpu and not GPU_AVAILABLE:
            raise MachSMT_GPU_Not_Available
        try:
            return mk_torch_regressor(use_gpu=use_gpu)
        except ValueError as ex:
            raise MachSMT_GPU_Not_Available
    elif core == 'xgboost':
        if use_gpu and not GPU_AVAILABLE:
            raise MachSMT_GPU_Not_Available
        return mk_xgboost_regressor(use_gpu=use_gpu)
    else: raise NotImplementedError
    