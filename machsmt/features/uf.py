
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


def uf_features(tokens):
    ufs = set()
    arity = []
    visit = []
    apps = {}
    for sexpr in tokens:
        # No need to traverse if no quantifiers present
        if isinstance(sexpr, tuple) and sexpr[0] == 'set-logic' \
                and sexpr[1] != 'ALL' \
                and 'UF' not in sexpr[1]:
            break
        # collect UFs (declare-fun ...)
        if sexpr and sexpr[0] == 'declare-fun':
            assert len(sexpr) == 4
            assert isinstance(sexpr[2], tuple)
            ufs.add(sexpr[1])
            arity.append(len(sexpr[2]))
        visit.append(sexpr)
        while visit:
            sexpr = visit.pop()
            if sexpr and isinstance(sexpr, tuple):
                if isinstance(sexpr[0], str) and sexpr[0] in ufs:
                    if sexpr[0] not in apps:
                        apps[sexpr[0]] = 0
                    apps[sexpr[0]] += 1
                    if len(sexpr) > 1:
                        visit.extend(sexpr[1:])
                else:
                    visit.extend(sexpr)
    avg_arity = sum(arity) / len(arity) if arity else 0
    avg_apps = sum(apps.values()) / len(apps) if apps else 0
    return [avg_arity, avg_apps]
