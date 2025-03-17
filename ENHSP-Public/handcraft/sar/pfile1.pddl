(define (problem sarp1)
    (:domain search_and_rescue)
    (:requirements :fluents)
    (:objects
        truck1 - truck
        city1 city2 - city
        person1 - person
        road1 road2 - road
    )
    (:init
        (= (refuels) 0)
        (= (fuel_consumed) 0)

        (located truck1 city1)
        (= (fuel truck1) 10000)
        (= (fuel_capacity truck1) 11000)
        (= (consumption truck1) 1)

        (located person1 city2)
        (wounded person1)

        (has_hospital city1)
        (has_shelter city2)

        (= (distance city1 city2) 450)
        (= (distance city2 city1) 450)

        (connected road1 city1)
        (connected road1 city2)
        (= (length road1) 550)

        (connected road2 city1)
        (connected road2 city2)
        (= (length road2) 200)
    )

    (:goal (and
        (saved person1)
    ))

    (:metric minimize (fuel_consumed))
)