#################
## DOMAIN INFO ##
#################

problem_name = 'Simple zeno'

#############
## FLUENTS ##
#############

Vp = [
    "located_person1_city2",
    "in_person1_plane1",
    "located_person1_city1",
    "located_plane1_city1",
    "located_plane1_city2",
]

#############
## ACTIONS ##
#############

actions = []
pre_p = {}
del_p = {}
add_p = {}

# A1-BOARD_PERSON1_PLANE1_CITY1
actions.append("board_person1_plane1_city1")
pre_p["board_person1_plane1_city1"] = {"located_person1_city1", "located_plane1_city1"}
del_p["board_person1_plane1_city1"] = {"located_person1_city1"}
add_p["board_person1_plane1_city1"] = {"in_person1_plane1"}

# A2-FLYSLOW_PLANE1_CITY1_CITY2
actions.append("flyslow_plane1_city1_city2")
pre_p["flyslow_plane1_city1_city2"] = {"located_plane1_city1"}
del_p["flyslow_plane1_city1_city2"] = {"located_plane1_city1"}
add_p["flyslow_plane1_city1_city2"] = {"located_plane1_city2"}

# A3-DEBARK_PERSON1_PLANE1_CITY2
actions.append("debark_person1_plane1_city2")
pre_p["debark_person1_plane1_city2"] = {"in_person1_plane1", "located_plane1_city2"}
del_p["debark_person1_plane1_city2"] = {"in_person1_plane1"}
add_p["debark_person1_plane1_city2"] = {"located_person1_city2"}


#############
## PROBLEM ##
#############

I = [
    "located_person1_city1",
    "located_plane1_city1",
]

Gp = [
	"located_person1_city2"
]