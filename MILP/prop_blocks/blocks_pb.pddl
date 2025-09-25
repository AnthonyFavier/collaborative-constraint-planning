(define (problem BLOCKS-10-0)
    (:domain BLOCKS)
    (:objects
        A B
    )
    (:init
        (CLEAR A)
        (CLEAR B)
        (ONTABLE A)
        (ONTABLE B)
        (HANDEMPTY)
    )
    (:goal
        (AND
            (ON A B)
        )
    )
)