(define (problem sarp1)
    (:domain search_and_rescue)
    (:objects
        truck1 - truck
        helicopter1 - helicopter
        city1 city2 city3 - city
        person1 person2 - person
        road121, road122, road231, road232 - road
    )
    (:init
        (located truck1 city1)
        (= (fuel truck1) 100)
        (= (fuel_capacity truck1) 300)
        (= (consumption truck1) 10)

        (located helicopter1 city1)
        (= (fuel helicopter1) 200)
        (= (fuel_capacity helicopter1) 500)
        (= (consumption helicopter1) 120)

        (located person1 city2)
        (wounded person1)

        (located person2 city3)

        (has_hospital city1)
        (has_shelter city2)
        (has_shelter city3)

        (= (distance city1 city2) 450)
        (= (distance city1 city3) 400)
        (= (distance city2 city3) 200)

        (connected road121 city1)
        (connected road121 city2)
        (= (length road121) 550)

        (connected road231 city2)
        (connected road231 city3)
        (= (length road231) 650)


        (has_heliport city1)
        (has_heliport city3)
    )

    (:goal (and
        (saved person1)
        (saved person2)
    ))

    (:metric minimize (fuel_consumed))
)