;; Enrico Scala (enricos83@gmail.com) and Miquel Ramirez (miquel.ramirez@gmail.com)
(define (domain zenotravel)
(:requirements :typing :fluents :equality)
(:types locatable city - object
	aircraft person - locatable)
(:predicates (located ?x - locatable  ?c - city)
             (in ?p - person ?a - aircraft))

(:action board
 :parameters (?p - person ?a - aircraft ?c - city)
 :precondition (and (located ?p ?c)
                 (located ?a ?c))
 :effect (and (not (located ?p ?c))
              (in ?p ?a)
                ))


(:action debark
 :parameters (?p - person ?a - aircraft ?c - city)
 :precondition (and (in ?p ?a)
                 (located ?a ?c))
 :effect (and (not (in ?p ?a))
              (located ?p ?c)
                ))

(:action flyslow
 :parameters (?a - aircraft ?c1 ?c2 - city)
 :precondition (and (located ?a ?c1)
                (not (= ?c1 ?c2))
                        )
 :effect (and (not (located ?a ?c1))
              (located ?a ?c2)
        )
)
                                  
(:action flyfast
 :parameters (?a - aircraft ?c1 ?c2 - city)
 :precondition (and (located ?a ?c1)
                (not (= ?c1 ?c2))
                 )
 :effect (and (not (located ?a ?c1))
              (located ?a ?c2)
	)
) 


)
