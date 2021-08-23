(set-info :smt-lib-version 2.6)
(set-info :category "crafted")
(set-info :source |Christoph M. Wintersteiger (cwinter@microsoft.com). Randomly generated floating-point testcases.|)
; Rounding mode: to positive
; Precision: double (11/53)
; X = -1.0395448422640456431764732769806869328022003173828125p-740 {- 178094136884781 -740 (-1.79741e-223)}
; Y = 1.292233266409337222313524762284941971302032470703125p-334 {+ 1316101629706354 -334 (3.69252e-101)}
; -1.0395448422640456431764732769806869328022003173828125p-740 = 1.292233266409337222313524762284941971302032470703125p-334 == 0

; bres: 0
; hwf : 0

(set-logic QF_FP)
(set-info :status unsat)
(define-sort FPN () (_ FloatingPoint 11 53))
(declare-fun x () FPN)
(declare-fun y () FPN)
(assert (= x (fp #b1 #b00100011011 #b0000101000011111100111000101110000111111111000101101)))
(assert (= y (fp #b0 #b01010110001 #b0100101011001111110011001010001000001000000001110010)))
(assert  (not (= (fp.eq x y) false)))
(check-sat)
(exit)
