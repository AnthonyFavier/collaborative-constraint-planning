
(define (domain example)
    (:requirements :strips :typing)
    (:types locatable - object
        package - locatable
        truck - locatable
        location - object
    )

    (:predicates
        (at ?p ?l)
        (in ?p ?t)
    )

    (:action load
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?p ?l) (at ?t ?l))
        :effect (and (in ?p ?t) (not (at ?p ?l)))
    )

    (:action unload
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (in ?p ?t) (at ?t ?l))
        :effect (and (at ?p ?l) (not (in ?p ?t)))
    )

    (:action drive
        :parameters (?t - truck ?l1 - location ?l2 - location)
        :precondition (and (at ?t ?l1))
        :effect (and (at ?t ?l2) (not (at ?t ?l1)))
    )

)