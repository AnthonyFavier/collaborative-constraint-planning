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
	
	(= (distance Denver Denver) 0)
	(= (distance Denver Dallas) 619)
	(= (distance Denver Washington) 565)
	(= (distance Denver Seattle) 886)
	(= (distance Denver Boston) 596)
	(= (distance Denver LosAngeles) 766)
	(= (distance Dallas Denver) 619)
	(= (distance Dallas Dallas) 0)
	(= (distance Dallas Washington) 561)
	(= (distance Dallas Seattle) 756)
	(= (distance Dallas Boston) 760)
	(= (distance Dallas LosAngeles) 980)
	(= (distance Washington Denver) 565)
	(= (distance Washington Dallas) 561)
	(= (distance Washington Washington) 0)
	(= (distance Washington Seattle) 657)
	(= (distance Washington Boston) 702)
	(= (distance Washington LosAngeles) 639)
	(= (distance Seattle Denver) 886)
	(= (distance Seattle Dallas) 756)
	(= (distance Seattle Washington) 657)
	(= (distance Seattle Seattle) 0)
	(= (distance Seattle Boston) 546)
	(= (distance Seattle LosAngeles) 510)
	(= (distance Boston Denver) 596)
	(= (distance Boston Dallas) 760)
	(= (distance Boston Washington) 702)
	(= (distance Boston Seattle) 546)
	(= (distance Boston Boston) 0)
	(= (distance Boston LosAngeles) 850)
	(= (distance LosAngeles Denver) 766)
	(= (distance LosAngeles Dallas) 980)
	(= (distance LosAngeles Washington) 639)
	(= (distance LosAngeles Seattle) 510)
	(= (distance LosAngeles Boston) 850)
	(= (distance LosAngeles LosAngeles) 0)

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