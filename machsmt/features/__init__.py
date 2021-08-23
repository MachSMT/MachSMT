from inspect import getmembers, isfunction

from . import arrays, bv, fp, real, integer, quantifiers, string, extra, uf

bonus_features = []
bonus_features += [o[1] for o in getmembers(arrays) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(bv) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(fp) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(real) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(integer) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(quantifiers) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(string) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(extra) if isfunction(o[1])]
bonus_features += [o[1] for o in getmembers(uf) if isfunction(o[1])]
