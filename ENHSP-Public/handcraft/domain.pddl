; All persons should be put into a shelter
; To do so, intervention forces should be with person and in a city with a shelter
; If the person is wounded, they should first go in an hospital before being moved to a shelter
; Trucks are cheaper and require roads
; Helicopter are expensive and require heliports

(define (domain search_and_rescue)
    (:requirements :typing :fluents :equality :disjunctive-preconditions :negative-preconditions)
    (:types
        locatable location - object
        vehicle person - locatable
        truck helicopter - vehicle
        city road - location
    )

    (:predicates
        (located ?x - locatable ?l - location)
        (in ?p - person ?v - vehicle)
        (has_hospital ?c - city)
        (has_shelter ?c - city)
        (has_heliport ?c - city)
        (wounded ?p - person)
        (saved ?p - person)
        (connected ?r - road ?c - city)
    )

    (:functions
        (fuel ?v - vehicle)
        (fuel_capacity ?v - vehicle)
        (consumption ?v - vehicle)
        (fuel_consumed)
        (distance ?c1 - city ?c2 - city)
        (length ?r)
        (refuels)
    )


    (:action drive_cr
        :parameters (?t - truck ?c - city ?r - road)
        :precondition (and 
            (located ?t ?c)
            (>= (- (fuel ?t) (* (length ?r) (consumption ?t))) 0)
            (connected ?r ?c)
        )
        :effect (and 
            (decrease (fuel ?t) (* (/ (length ?r) 2) (consumption ?t)) )
            (increase (fuel_consumed) (/ (* (length ?r) 2) (consumption ?t)))
            (not (located ?t ?c))
            (located ?t ?r)
        )
    )

    (:action drive_rc
        :parameters (?t - truck ?r - road ?c - city)
        :precondition (and 
            (located ?t ?r)
            (>= (- (fuel ?t) (* (/ (length ?r) 2) (consumption ?t))) 0)
            (connected ?r ?c)
        )
        :effect (and 
            (decrease (fuel ?t) (* (/ (length ?r) 2) (consumption ?t)) )
            (increase (fuel_consumed) (* (/ (length ?r) 2) (consumption ?t)))
            (not (located ?t ?r))
            (located ?t ?c)
        )
    )
    
    (:action fly
        :parameters (?h - helicopter ?c1 - city ?c2 - city)
        :precondition (and 
            (located ?h ?c1)
            (not (= ?c1 ?c2))
            (>= (- (fuel ?h) (* (distance ?c1 ?c2) (consumption ?h))) 0)
            (has_heliport ?c2)
        )
        :effect (and 
            (decrease (fuel ?h) (* (distance ?c1 ?c2) (consumption ?h)) )
            (increase (fuel_consumed) (* (distance ?c1 ?c2) (consumption ?h)) )
            (not (located ?h ?c1))
            (located ?h ?c2)
        )
    )
    
    (:action board
        :parameters (?p - person ?v - vehicle ?c - city)
        :precondition (and 
            (located ?v ?c)
            (located ?p ?c)
            (not (in ?p ?v))
            (not (saved ?p))
        )
        :effect (and 
            (not (located ?p ?c))
            (in ?p ?v)
        )
    )
    
    (:action refuel
        :parameters (?v - vehicle ?c - city)
        :precondition (and 
            (located ?v ?c)
            (< (fuel ?v) (fuel_capacity ?v))
        )
        :effect (and 
            (assign (fuel ?v) (fuel_capacity ?v))
            (increase (refuels) 1)
        )
    )
    
    (:action drop_at_hospital
        :parameters (?p - person ?v - vehicle ?c - city)
        :precondition (and 
            (in ?p ?v)
            (located ?v ?c)
            (wounded ?p)
            (has_hospital ?c)
        )
        :effect (and 
            (not (in ?p ?v))
            (located ?p ?c)
            (not (wounded ?p))
        )
    )
    
    (:action drop_at_shelter
        :parameters (?p - person ?v - vehicle ?c - city)
        :precondition (and 
            (in ?p ?v)
            (located ?v ?c)
            (not (wounded ?p))
            (has_shelter ?c)
        )
        :effect (and 
            (not (in ?p ?v))
            (located ?p ?c)
            (saved ?p)
        )
    )
    
)