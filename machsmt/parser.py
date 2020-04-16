
from machsmt.tokenize-sexpr import SExprTokenizer

class SMT2_Input:
    def __init__(self,input_file):
        with open(input_file) as infile:
            self.tokenized = SExprTokenizer(infile.read())