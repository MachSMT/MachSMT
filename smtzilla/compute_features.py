from inspect import getmembers, isfunction
import smtzilla.extra_features as extra_features
from smtzilla.keywords import keyword_list
import time
kw2indx = dict( (keyword_list[i],i) for i in range(len(keyword_list)))

def get_core_features(file_path):
    tic = time.time()
    features = [0.0] * len(keyword_list)
    n = 0
    v = -1.0
    with open(file_path,'r') as file:
        for line in file.readlines():
            line = line.replace('(', ' ( ')
            line = line.replace(')', ' ) ')
            if line.find(';') != -1:
                line = line[:line.find(';')]
            line = line.split()
            for t in line:
                if t in kw2indx:
                    features[kw2indx[t]] += 1.0
                n+=1
            if n > 1000 and time.time() - tic > 5.0:
                v = 1.0
                break

        features.append(n)
        features.append(v)
    return features

def get_features(file_path,theory,track):
    features = get_core_features(file_path)

    functions = [o for o in getmembers(smtzilla.extra_features as extra_features) if isfunction(o[1])]
    for f smtzilla.in functions:
        v = f(file_path,theory,track)
        if v != None:
            features.append(v)
    return features

def get_check_sat(file_path):
    ret = 0
    with open(file_path,'r') as file:
        for line in file.readlines():
            line = line.replace('(', ' ( ')
            line = line.replace(')', ' ) ')
            if line.find(';') != -1:
                line = line[:line.find(';')]
            line = line.split()
            for t in line:
                if t == 'check-sat':
                    ret += 1.0
    return ret