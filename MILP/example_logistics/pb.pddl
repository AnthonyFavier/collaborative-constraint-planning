(define (problem example-10-0)
    (:domain example)
    (:objects
        loc1 loc2 - location
        p1 - package
        t1 - truck
    )
    (:init
        (at p1 loc1)
        (at t1 loc1)
    )
    (:goal
        (AND
            (at p1 loc2)
        )
    )
)