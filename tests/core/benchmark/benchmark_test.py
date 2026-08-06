import unittest
import os
import tempfile
from machsmt.benchmark import Benchmark
from machsmt.benchmark.tokenize_sexpr import SExprTokenizer


def nav_to_data_dir():
    loc = os.path.dirname(os.path.abspath(__file__))
    os.chdir(loc)
    os.chdir('..')  # exit db
    os.chdir('..')  # exit core
    os.chdir('data')


class BenchmarkTest(unittest.TestCase):
    def test_init_1(self):
        nav_to_data_dir()
        a = Benchmark('benchmarks/a.smt2')
        self.assertEqual(a.logic, 'UNPARSED')
        self.assertTrue(not a.parsed)

    def test_init_2(self):
        nav_to_data_dir()
        with self.assertRaises(FileNotFoundError):
            Benchmark('asdf')

    def test_logic(self):
        nav_to_data_dir()
        a = Benchmark('benchmarks/a.smt2')
        a.parse()
        self.assertEqual(a.get_logic(), 'QF_FP')

    def test_compute_features(self):
        nav_to_data_dir()
        a = Benchmark('benchmarks/a.smt2')
        self.assertEqual(type(a.get_features()), list)
        self.assertEqual(len(a.get_features()), 0)

        a.parse()

        self.assertEqual(len(a.get_features()) > 100, True)
        self.assertEqual(type(a.get_features()), list)


commented_smt2 = '''; a comment before any s-expression
(set-logic QF_LIA)
(
  ; a comment immediately after an opening paren
  declare-fun x () Int)
(assert (> x 0)) ; an end of line comment
(assert (= s "; not a comment, this is a string literal"))
(check-sat)
; a trailing comment with no newline at the end of the file'''


class SExprTokenizerTest(unittest.TestCase):
    def tokenize(self, contents):
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.smt2', delete=False)
        tmp.write(contents)
        tmp.close()
        try:
            return [sexpr for sexpr in SExprTokenizer(tmp.name)]
        finally:
            os.remove(tmp.name)

    def test_comments_are_discarded(self):
        self.assertEqual(self.tokenize(commented_smt2), [
            ('set-logic', 'QF_LIA'),
            ('declare-fun', 'x', (), 'Int'),
            ('assert', ('>', 'x', '0')),
            ('assert', ('=', 's', '"; not a comment, this is a string literal"')),
            ('check-sat',),
        ])

    def test_comment_only_file(self):
        self.assertEqual(self.tokenize('; nothing but a comment\n'), [])

if __name__ == '__main__':
    unittest.main()
