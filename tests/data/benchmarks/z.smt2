(set-info :smt-lib-version 2.6)
(set-logic QF_BV)
(set-info :source |
Hand-crafted bit-vector benchmarks.  Some are from the SVC benchmark suite.
Contributed by Vijay Ganesh (vganesh@stanford.edu).  Translated into SMT-LIB
format by Clark Barrett using CVC3.

|)
(set-info :category "crafted")
(set-info :status unsat)
(assert (not (= (concat (ite (not (= (ite false (_ bv1 1) (_ bv0 1)) (_ bv1 1))) (_ bv1 1) (_ bv0 1)) (_ bv0 1)) (_ bv2 2))))
(check-sat)
(exit)
