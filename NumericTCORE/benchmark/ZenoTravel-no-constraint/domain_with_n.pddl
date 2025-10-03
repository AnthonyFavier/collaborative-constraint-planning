;; Enrico Scala (enricos83@gmail.com) and Miquel Ramirez (miquel.ramirez@gmail.com)
(define (domain zenotravel)
        ;(:requirements :typing :fluents)
        (:types
                locatable city - object
                aircraft person - locatable
        )
        (:predicates
                (located ?x - locatable ?c - city)
                (in ?p - person ?a - aircraft)
        )
        (:functions
                (fuel ?a - aircraft)
                (distance ?c1 - city ?c2 - city)
                (slow_burn ?a - aircraft)
                (fast_burn ?a - aircraft)
                (capacity ?a - aircraft)
                (total_fuel_used)
                (onboard ?a - aircraft)
                (zoom_limit ?a - aircraft)

                (n_board ?p - person ?a - aircraft ?c - city)
                (n_debark ?p - person ?a - aircraft ?c - city)
                (n_flyslow ?a - aircraft ?c1 ?c2 - city)
                (n_flyfast ?a - aircraft ?c1 ?c2 - city)
                (n_refuel ?a - aircraft)
        )

        (:action board
                :parameters (?p - person ?a - aircraft ?c - city)
                :precondition (and (located ?p ?c)
                        (located ?a ?c))
                :effect (and (not (located ?p ?c))
                        (in ?p ?a)
                        (increase (onboard ?a) 1)
                        (increase (n_board ?p ?a ?c) 1))
        )

        (:action debark
                :parameters (?p - person ?a - aircraft ?c - city)
                :precondition (and (in ?p ?a)
                        (located ?a ?c))
                :effect (and (not (in ?p ?a))
                        (located ?p ?c)
                        (decrease (onboard ?a) 1)
                        (increase (n_debark ?p ?a ?c) 1))
        )

        (:action flyslow
                :parameters (?a - aircraft ?c1 ?c2 - city)
                :precondition (and (located ?a ?c1)
                        (>= (fuel ?a)
                                (* (distance ?c1 ?c2) (slow_burn ?a))))
                :effect (and (not (located ?a ?c1))
                        (located ?a ?c2)
                        (increase
                                (total_fuel_used)
                                (* (distance ?c1 ?c2) (slow_burn ?a)))
                        (decrease
                                (fuel ?a)
                                (* (distance ?c1 ?c2) (slow_burn ?a)))
                        (increase (n_flyslow ?a ?c1 ?c2) 1))
        )

        (:action flyfast
                :parameters (?a - aircraft ?c1 ?c2 - city)
                :precondition (and (located ?a ?c1)
                        (>= (fuel ?a)
                                (* (distance ?c1 ?c2) (fast_burn ?a)))
                        (<= (onboard ?a) (zoom_limit ?a)))
                :effect (and (not (located ?a ?c1))
                        (located ?a ?c2)
                        (increase
                                (total_fuel_used)
                                (* (distance ?c1 ?c2) (fast_burn ?a)))
                        (decrease
                                (fuel ?a)
                                (* (distance ?c1 ?c2) (fast_burn ?a)))
                        (increase (n_flyfast ?a ?c1 ?c2) 1))
        )

        (:action refuel
                :parameters (?a - aircraft)
                :precondition (and (> (capacity ?a) (fuel ?a))

                )
                :effect (and (assign (fuel ?a) (capacity ?a))
                        (increase (n_refuel ?a) 1))
        )

)