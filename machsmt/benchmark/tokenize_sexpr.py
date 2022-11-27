#!/usr/bin/env python

import argparse
import pdb


class SExprTokenizer:
    def __init__(self, infile):
        self.file = open(infile, 'r')

    def __iter__(self):
        return self

    def __next__(self):
        token = self.tokenize()
        if token is None:
            self.file.close()
            raise StopIteration
        return token

    def tokenize(self):
        exprs = []
        cur_expr = None
        cur_quoted_symbol = []
        cur_comment = []
        cur_string_literal = []
        cur_token = None
        whitespace_chars = [' ', '\t', '\n']

        while True:
            char = self.file.read(1)
            if not char:
                break

            # Handle string literals
            if (char == '"' or cur_string_literal) and not cur_comment:
                cur_string_literal.append(char)
                # TODO: Escaped quotes "A "" B "" C" is one string literal
                if char == '"' and len(cur_string_literal) > 1:
                    assert cur_expr is not None
                    cur_expr.append(''.join(cur_string_literal))
                    cur_string_literal = []
                continue

            # Handle piped symbols
            if char == '|' or cur_quoted_symbol:
                if len(cur_comment) > 0:
                    continue
                cur_quoted_symbol.append(char)
                if char == '|' and len(cur_quoted_symbol) > 1:
                    # Piped symbols only appear in s-expressions
                    if cur_expr is None:
                        cur_expr = []
                    cur_expr.append(''.join(cur_quoted_symbol))
                    cur_quoted_symbol = []
                continue

            # Handle comments
            if char == ';' or cur_comment:
                cur_comment.append(char)
                if char == '\n':
                    comment = ''.join(cur_comment)
                    cur_comment = []
                    if cur_expr:
                        cur_expr.append(comment)
                    else:
                        return comment
                continue

            # Open s-expression
            if char == '(':
                # Check if token is not yet consumed
                if cur_token is not None:
                    cur_expr.append(''.join(cur_token))
                    cur_token = None

                cur_expr = []
                exprs.append(cur_expr)

            # Close s-expression
            elif char == ')':
                assert exprs
                assert cur_expr == exprs[-1]
                cur_expr = exprs.pop()

                # Check if token is not yet consumed
                if cur_token is not None:
                    cur_expr.append(''.join(cur_token))
                    cur_token = None

                # Do we have nested s-expressions?
                if exprs:
                    exprs[-1].append(tuple(cur_expr))
                    cur_expr = exprs[-1]
                else:
                    return tuple(cur_expr)

            # Start new token
            elif cur_token is None and char not in whitespace_chars:
                cur_token = [char]

            # Close current token
            elif cur_token and char in whitespace_chars:
                token = ''.join(cur_token)

                # Append token to current sexpr
                if cur_expr is not None:
                    cur_expr.append(token)
                else:
                    return token

                cur_token = None

            # Append to current token
            elif cur_token is not None:
                cur_token.append(char)
        assert not exprs
        assert cur_token is None
        return None

    def __del__(self):
        self.file.close()
        
def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    args = ap.parse_args()

    tokenizer = SExprTokenizer(args.input)

    for sexpr in tokenizer:
        print(sexpr)


if __name__ == '__main__':
    main()
