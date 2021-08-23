
'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string

OUTPUT

    A single number or an iterable of numbers

'''


def array_features(tokens):
    store_chains = []
    visit = []
    arrays = {}

    for sexpr in tokens:
        # No need to traverse if no arrays present
        if isinstance(sexpr, tuple) and sexpr[0] == 'set-logic' \
                and sexpr[1] != 'ALL' \
                and not sexpr[1].startswith('A') \
                and not sexpr[1].startswith('QF_A'):
            break

        visit.append(sexpr)
        while visit:
            token = visit.pop()
            if isinstance(token, tuple):
                # avg. number of selects per array feature
                if token and token[0] == 'select':
                    array = token[1]
                    if array not in arrays:
                        arrays[array] = 0
                    arrays[array] += 1
                    visit.extend(token)
                # avg. store chain depth feature
                elif token and token[0] == 'store':
                    num_stores = 0
                    l = token
                    while l[0] == 'store':
                        assert len(l) == 4
                        num_stores += 1
                        visit.append(l[2])
                        visit.append(l[3])
                        l = l[1]
                    if num_stores > 1:
                        store_chains.append(num_stores)
                else:
                    visit.extend(token)

    features = []
    if store_chains:
        features.append(sum(store_chains) / len(store_chains))
    else:
        features.append(0)

    num_selects = [v for k, v in arrays.items()]
    if num_selects:
        features.append(sum(num_selects) / len(num_selects))
    else:
        features.append(0)

    return features
