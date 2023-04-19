(set-info :smt-lib-version 2.6)
(set-info :category "crafted")
(set-info :source |Christoph M. Wintersteiger (cwinter@microsoft.com). Randomly generated floating-point testcases.|)
; Rounding mode: to positive
; Precision: double (11/53)
; X = -1.3180485843723144245842604505014605820178985595703125p-150 {- 1432363486064869 -150 (-9.2349e-046)}
; Y = -1.07364176369318276016429081209935247898101806640625p863 {- 331653019527524 863 (-6.60307e+259)}
; -1.3180485843723144245842604505014605820178985595703125p-150 = -1.07364176369318276016429081209935247898101806640625p863 == 0

; bres: 0
; hwf : 0

(set-logic QF_FP)
(set-info :status unsat)
(define-sort FPN () (_ FloatingPoint 11 53))
(declare-fun x () FPN)
(declare-fun y () FPN)
(assert (= x (fp #b1 #b01101101001 #b0101000101101011101000011100110001101011000011100101)))
(assert (= y (fp #b1 #b11101011110 #b0001001011011010001011111100011010101110100101100100)))
(assert  (not (= (fp.eq x y) false)))
(check-sat)
(exit)
