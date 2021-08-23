
'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string

OUTPUT

    A single number or an iterable of numbers

'''


def quantifier_features(tokens):

    num_forall_vars = 0
    num_exists_vars = 0
    quant_chains = []

    visit = []
    for sexpr in tokens:
        # No need to traverse if no quantifiers present
        if isinstance(sexpr, tuple) and sexpr[0] == 'set-logic' \
                and sexpr[1] != 'ALL' \
                and sexpr[1].startswith('QF_'):
            break

        visit.append(sexpr)
        while visit:
            sexpr = visit.pop()
            if sexpr and isinstance(sexpr, tuple):
                if sexpr[0] in ('forall', 'exists'):
                    # Count total number of exists and forall variables, and their
                    # ratio.
                    if sexpr[0] == 'forall':
                        num_forall_vars += len(sexpr[1])
                        visit.append(sexpr[2])
                    else:
                        num_exists_vars += len(sexpr[1])
                        visit.append(sexpr[2])

                    # Determine average quantifier nesting level
                    num_quants = 1
                    sexpr = sexpr[2]
                    while isinstance(sexpr, tuple) and sexpr[0] in ('exists', 'forall'):
                        assert len(sexpr) == 3
                        num_quants += 1
                        sexpr = sexpr[2]
                    quant_chains.append(num_quants)
                else:
                    visit.extend(sexpr)

    features = [
        num_forall_vars,
        num_exists_vars,
        num_exists_vars / num_forall_vars if num_forall_vars > 0 else 0
    ]
    features.append(sum(quant_chains) / len(quant_chains)
                    if quant_chains else 0)

    return features
