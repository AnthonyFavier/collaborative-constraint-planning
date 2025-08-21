(define (problem ZTRAVEL-3-10)
(:domain zenotravel)
(:objects
	plane1 - aircraft
	plane2 - aircraft
	plane3 - aircraft
	person1 - person
	person2 - person
	person3 - person
	person4 - person
	person5 - person
	person6 - person
	person7 - person
	person8 - person
	person9 - person
	person10 - person

	Denver - city
	Dallas - city
	Washington - city
	Seattle - city
	Boston - city
	LosAngeles - city
	)
(:init
	(located plane1 Boston)
	(= (capacity plane1) 2326)
	(= (fuel plane1) 205)
	(= (slow-burn plane1) 1)
	(= (fast-burn plane1) 2)
	(= (onboard plane1) 0)
	(= (zoom-limit plane1) 10)
	(located plane2 Washington)
	(= (capacity plane2) 12132)
	(= (fuel plane2) 1469)
	(= (slow-burn plane2) 4)
	(= (fast-burn plane2) 9)
	(= (onboard plane2) 0)
	(= (zoom-limit plane2) 9)
	(located plane3 Seattle)
	(= (capacity plane3) 5204)
	(= (fuel plane3) 1532)
	(= (slow-burn plane3) 2)
	(= (fast-burn plane3) 7)
	(= (onboard plane3) 0)
	(= (zoom-limit plane3) 8)
	(located person1 Dallas)
	(located person2 Washington)
	(located person3 Dallas)
	(located person4 Boston)
	(located person5 LosAngeles)
	(located person6 Dallas)
	(located person7 Denver)
	(located person8 Washington)
	(located person9 Dallas)
	(located person10 LosAngeles)
	
	(= (distance Denver Dallas) 1068)
	(= (distance Dallas Denver) 1068)
	(= (distance Denver Washington) 2397)
	(= (distance Washington Denver) 2397)
	(= (distance Denver Boston) 2839)
	(= (distance Boston Denver) 2839)
	(= (distance Denver Seattle) 1641)
	(= (distance Seattle Denver) 1641)
	(= (distance Denver LosAngeles) 1327)
	(= (distance LosAngeles Denver) 1327)
	(= (distance Dallas Washington) 1912)
	(= (distance Washington Dallas) 1912)
	(= (distance Dallas Boston) 2505)
	(= (distance Boston Dallas) 2505)
	(= (distance Dallas Seattle) 2705)
	(= (distance Seattle Dallas) 2705)
	(= (distance Dallas LosAngeles) 1989)
	(= (distance LosAngeles Dallas) 1989)
	(= (distance Washington Boston) 628)
	(= (distance Boston Washington) 628)
	(= (distance Washington Seattle) 3736)
	(= (distance Seattle Washington) 3736)
	(= (distance Washington LosAngeles) 3693)
	(= (distance LosAngeles Washington) 3693)
	(= (distance Boston Seattle) 4005)
	(= (distance Seattle Boston) 4005)
	(= (distance Boston LosAngeles) 4153)
	(= (distance LosAngeles Boston) 4153)
	(= (distance Seattle LosAngeles) 1548)
	(= (distance LosAngeles Seattle) 1548)

	(= (total-fuel-used) 0)
)
(:goal (and
	(located plane1 Boston)
	(located person1 Boston)
	(located person2 LosAngeles)
	(located person3 Boston)
	(located person4 Denver)
	(located person5 Washington)
	(located person6 Seattle)
	(located person8 Denver)
	(located person9 Seattle)
	(located person10 Boston)
	))

(:metric minimize (total-fuel-used))





)