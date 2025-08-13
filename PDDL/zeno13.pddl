; Describe the problem Zeno13 from the ZenoTravel domain
(define (problem ZENO13)
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
	boston - city
	newyork - city
	washington - city
	portland - city
	philadelphie - city
	atlanta - city
	)
(:init
	(located plane1 philadelphie)
	(= (capacity plane1) 2326)
	(= (fuel plane1) 205)
	(= (slow-burn plane1) 1)
	(= (fast-burn plane1) 2)
	(= (onboard plane1) 0)
	(= (zoom-limit plane1) 10)
	(located plane2 washington)
	(= (capacity plane2) 12132)
	(= (fuel plane2) 1469)
	(= (slow-burn plane2) 4)
	(= (fast-burn plane2) 9)
	(= (onboard plane2) 0)
	(= (zoom-limit plane2) 9)
	(located plane3 portland)
	(= (capacity plane3) 5204)
	(= (fuel plane3) 1532)
	(= (slow-burn plane3) 2)
	(= (fast-burn plane3) 7)
	(= (onboard plane3) 0)
	(= (zoom-limit plane3) 8)
	(located person1 newyork)
	(located person2 washington)
	(located person3 newyork)
	(located person4 philadelphie)
	(located person5 atlanta)
	(located person6 newyork)
	(located person7 boston)
	(located person8 washington)
	(located person9 newyork)
	(located person10 atlanta)
	(= (distance boston boston) 0)
	(= (distance boston newyork) 619)
	(= (distance boston washington) 565)
	(= (distance boston portland) 886)
	(= (distance boston philadelphie) 596)
	(= (distance boston atlanta) 766)
	(= (distance newyork boston) 619)
	(= (distance newyork newyork) 0)
	(= (distance newyork washington) 561)
	(= (distance newyork portland) 756)
	(= (distance newyork philadelphie) 760)
	(= (distance newyork atlanta) 980)
	(= (distance washington boston) 565)
	(= (distance washington newyork) 561)
	(= (distance washington washington) 0)
	(= (distance washington portland) 657)
	(= (distance washington philadelphie) 702)
	(= (distance washington atlanta) 639)
	(= (distance portland boston) 886)
	(= (distance portland newyork) 756)
	(= (distance portland washington) 657)
	(= (distance portland portland) 0)
	(= (distance portland philadelphie) 546)
	(= (distance portland atlanta) 510)
	(= (distance philadelphie boston) 596)
	(= (distance philadelphie newyork) 760)
	(= (distance philadelphie washington) 702)
	(= (distance philadelphie portland) 546)
	(= (distance philadelphie philadelphie) 0)
	(= (distance philadelphie atlanta) 850)
	(= (distance atlanta boston) 766)
	(= (distance atlanta newyork) 980)
	(= (distance atlanta washington) 639)
	(= (distance atlanta portland) 510)
	(= (distance atlanta philadelphie) 850)
	(= (distance atlanta atlanta) 0)
	(= (total-fuel-used) 0)
)
(:goal (and
	(located plane1 philadelphie)
	(located person1 philadelphie)
	(located person2 atlanta)
	(located person3 philadelphie)
	(located person4 boston)
	(located person5 washington)
	(located person6 portland)
	(located person8 boston)
	(located person9 portland)
	(located person10 philadelphie)
	))

(:metric minimize (total-fuel-used))


)