
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
#  - avg/mean quantifier nesting level of formulas

def forall_exists_vars(tokens):
    num_forall_vars = 0
    num_exists_vars = 0
    visit = []
    for token in tokens:
        visit.append(token)

        while visit:
            token = visit.pop()
            if isinstance(token, list):
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


