
'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string

OUTPUT

    A single number or an iterable of numbers

'''

# Determine average arity and number of applications of UFs
def avg_UF_arity_and_applications(tokens):
    ufs = []
    arity = []
    visit = []
    for token in tokens:
        visit.append(token)
        while visit:
            token = visit.pop()
            if isinstance(token, list):
                if token and token[0] == 'declare-fun':
                    # assert(len(token) == 4)
                    assert(isinstance(token[2], list))
                    ufs.append(token[1])
                    arity.append(len(token[2]))
                else:
                    visit.extend(t for t in token)
    len_arity = len(arity)
    avg_arity = sum(arity) / len(arity) if len_arity > 0 else 0
    apps = {}
    for token in tokens:
        visit.append(token)
        while visit:
            token = visit.pop()
            if isinstance(token, list):
                if token and token[0] in ufs:
                    if token[0] in apps:
                        apps[token[0]] += 1
                    else:
                       apps[token[0]] = 0
                    if len(token) > 1: visit.append(token[1])
                else:
                    visit.extend(t for t in token)
    len_apps = len(apps)
    avg_apps = sum(apps.values()) / len(apps) if len_apps > 0 else 0
    return [avg_arity, avg_apps]

