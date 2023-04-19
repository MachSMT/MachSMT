(set-info :smt-lib-version 2.6)
(set-logic QF_BV)
(set-info :source |
Hand-crafted bit-vector benchmarks.  Some are from the SVC benchmark suite.
Contributed by Vijay Ganesh (vganesh@stanford.edu).  Translated into SMT-LIB
format by Clark Barrett using CVC3.

|)
(set-info :category "crafted")
(set-info :status unsat)
(assert (let ((?v_0 (= ((_ extract 1 1) (_ bv1 3)) (_ bv1 1))) (?v_1 (= ((_ extract 1 1) (_ bv7 3)) (_ bv1 1)))) (let ((?v_4 (or (and (not ?v_0) ?v_1) (and ?v_0 (not ?v_1)))) (?v_2 (= ((_ extract 0 0) (_ bv1 3)) (_ bv1 1))) (?v_3 (= ((_ extract 0 0) (_ bv7 3)) (_ bv1 1)))) (let ((?v_5 (= (ite (or (and ?v_2 ?v_3) (and (or (and (not ?v_2) ?v_3) (and ?v_2 (not ?v_3))) (= (_ bv0 1) (_ bv1 1)))) (_ bv1 1) (_ bv0 1)) (_ bv1 1)))) (not (= (ite (or (and (not ?v_4) ?v_5) (and ?v_4 (not ?v_5))) (_ bv1 1) (_ bv0 1)) (_ bv0 1)))))))
(check-sat)
(exit)
