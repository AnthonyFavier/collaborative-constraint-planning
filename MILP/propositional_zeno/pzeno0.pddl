(define (problem ZTRAVEL-1-2)
(:domain zenotravel)
(:objects
	plane1 - aircraft
	person1 - person
	city1 - city
	city2 - city
	)
(:init
	(located plane1 city1)
	(located person1 city1)

)
(:goal (and	
	(located person1 city2)
	))


)