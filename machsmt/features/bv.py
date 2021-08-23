
'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string

OUTPUT

    A single number or an iterable of numbers

'''

import statistics


def feature_adder_chains(tokens):

    # Traverse adders only, appends adder leafs to to_visit stack.
    def traverse_adders(adder, lets, chains, to_visit, lets_visit_cache):
        visited = dict()
        visit = []
        visit.append(adder)
        num_adds = 0
        while visit:
            cur = visit.pop()
            if isinstance(cur, str) and \
               cur in lets and cur not in lets_visit_cache:
                lets_visit_cache.add(cur)
                cur = lets.get(cur)
            if isinstance(cur, tuple):
                # avg. store chain depth feature
                if cur and cur[0] == 'bvadd':
                    # down-traversal
                    if cur not in chains:
                        chains[cur] = 0
                        visit.append(cur)
                        visit.extend(cur)
                    # up-traversal
                    elif chains[cur] == 0:
                        chains[cur] = 1
                        for c in cur[1:]:
                            c = lets.get(c, c)
                            if c in chains:
                                chains[cur] += chains[c]
                else:
                    to_visit.extend(cur)

    adder_chains = []
    visit = []
    chains = {}  # maps adder to number of nested adders below
    for sexpr in tokens:
        # No need to traverse if no bit-vectors present
        if isinstance(sexpr, tuple) and sexpr[0] == 'set-logic' \
                and sexpr[1] != 'ALL' \
                and 'BV' not in sexpr[1]:
            break

        lets = {}
        lets_visit_cache = set()
        visit.append(sexpr)
        while visit:
            cur = visit.pop()
            # Only visit let symbols once
            if isinstance(cur, str) and \
               cur in lets and cur not in lets_visit_cache:
                lets_visit_cache.add(cur)
                cur = lets.get(cur)
            if isinstance(cur, tuple):
                # map symbols to sexpr (let binder)
                if cur and cur[0] == 'let':
                    for letbind in cur[1]:
                        lets[letbind[0]] = letbind[1]
                    visit.append(cur[-1])
                # avg. store chain depth feature
                elif cur and cur[0] == 'bvadd':
                    traverse_adders(cur, lets, chains, visit, lets_visit_cache)
                    if chains[cur] > 1:
                        adder_chains.append(chains[cur])
                else:
                    visit.extend(cur)

    features = []
    if adder_chains:
        features.append(statistics.mean(adder_chains))
        features.append(statistics.median(adder_chains))
    else:
        features.append(0)
        features.append(0)

    return features
