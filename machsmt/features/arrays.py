
'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string

OUTPUT

    A single number or an iterable of numbers

'''

# TODO
#  - avg/mean reads per array

# Count average depth of store chains
def count_avg_store_chain_depth(tokens):
    store_chains = []
    visit = []
    for token in tokens:
        visit.append(token)

        while visit:
            token = visit.pop()
            if isinstance(token, list):
                if token and token[0] == 'store':
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
                    visit.extend(t for t in token)
    len_stores = len(store_chains)
    return sum(store_chains) / len(store_chains) if len_stores > 0 else 0
