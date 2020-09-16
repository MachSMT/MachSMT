
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
#  - avg/mean UF applications per function

# Determine average arity of UFs
def avg_UF_arity(tokens):
    ufs = []
    visit = []
    for token in tokens:
        visit.append(token)
        while visit:
            token = visit.pop()
            if isinstance(token, list):
                if token and token[0] == 'declare-fun':
                    ufs.append(len(token[1]))
                else:
                    visit.extend(t for t in token)
    len_ufs = len(ufs)
    return sum(ufs) / len(ufs) if len_ufs > 0 else 0

