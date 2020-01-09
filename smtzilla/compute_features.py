from inspect import getmembers, isfunction
import smtzilla.extra_features as extra_features
from smtzilla.keywords import keyword_list
import time
kw2indx = dict( (keyword_list[i],i) for i in range(len(keyword_list)))
cached_counts = {}
cached_checksats = {}

COUNT_TIMEOUT = 1.0

def get_syntactic_count_features(file_path):
    if file_path in cached_counts:
        print("Cache :)")
        return cached_counts[file_path]
    tic = time.time()
    features = [0.0] * len(keyword_list)
    n = 0
    v = -1.0
    with open(file_path,'r') as file:
        for line in file:
            line = line.replace('(', ' ( ')
            line = line.replace(')', ' ) ')
            if line.find(';') != -1:
                line = line[:line.find(';')]
            line = line.split()
            for t in line:
                if t in kw2indx:
                    features[kw2indx[t]] += 1.0
                n+=1
            if time.time() - tic > COUNT_TIMEOUT:
                v = 1.0
                break
        features.append(n)      ##Total Counts
        features.append(v)      ##Timeout?
    cached_counts[file_path] = features
    return features

def get_features(file_path,theory,track):
    features = get_syntactic_count_features(file_path)

    functions = [o for o in getmembers(extra_features) if isfunction(o[1])]
    for f in functions:
        tic = time.time()
        v = f(file_path,theory,track)
        if v != None:
            features.append(v)
            features.append(time.time() - tic)
    return features

def get_feature_names():
    ret = []
    for kw in keyword_list:
        ret.append('COUNT_' + kw)
    ret.append('COUNT_N')
    ret.append('COUNT_TIMEOUT')
    functions = [o for o in getmembers(extra_features) if isfunction(o[1])]
    for foo in functions:
        ret.append(foo.__name__)
        ret.append(foo.__name__ + '_TIME')
    return ret

def get_check_sat(file_path):
    if file_path in cached_checksats:
        return cached_checksats[file_path]
    ret = 0
    with open(file_path,'r') as file:
        for line in file:
            if line.find(';') != -1:
                line = line[:line.find(';')]
            ret += line.count('check-sat')
    cached_checksats[file_path] = ret
    return ret