
'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string

OUTPUT

    A single number or an iterable of numbers

'''

# Count total number of exists and forall variables, and their ratio
def forall_exists_vars(tokens):
    num_forall_vars = 0
    num_exists_vars = 0
    visit = []
    cache = set()
    for token in tokens:
        visit.append(token)

        while visit:
            token = visit.pop()
            if token in cache:
                continue
            cache.add(token)
            if isinstance(token, tuple):
                if token and token[0] == 'forall':
                    num_forall_vars += len(token[1])
                    visit.append(token[2])
                elif token and token[0] == 'exists':
                    num_exists_vars += len(token[1])
                    visit.append(token[2])
                else:
                    visit.extend(t for t in token)
    return [
        num_forall_vars,
        num_exists_vars,
        num_exists_vars / num_forall_vars if num_forall_vars > 0 else 0
      ]

# Determine average quantifier nesting level
def avg_nesting_level(tokens):
    quant_chains = []
    visit = []
    cache = set()
    for token in tokens:
        visit.append(token)
        while visit:
            token = visit.pop()
            if token in cache:
                continue
            cache.add(token)
            if isinstance(token, tuple):
                if token and (token[0] == 'exists' or token[0] == 'forall'):
                    num_quants = 0
                    t = token
                    while t[2][0] == 'exists' or t[2][0] == 'forall':
                        assert len(t) == 3
                        num_quants += 1
                        t = t[2]
                    quant_chains.append(num_quants)
                else:
                    visit.extend(t for t in token)
    len_quants = len(quant_chains)
    return sum(quant_chains) / len(quant_chains) if len_quants > 0 else 0
