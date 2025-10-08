
(define (problem instance_2)
  (:domain fn-counters)
  (:objects
    c0 c1 - counter
  )

  (:init
    (= (value_counter c0) 7)
	(= (value_counter c1) 1)
	(= (max_int) 4)
  )

  (:goal (and 
    (>= (value_counter c0) 2)
    (<= (value_counter c0) 4)

    ; (= (value_counter c0) 2)
    (= (value_counter c1) 2)
  ))


)