#################
## DOMAIN INFO ##
#################

#############
## FLUENTS ##
#############

Vp = [
    "on_A_B",
    "ontable_A",
    "ontable_B",
    "clear_A",
    "clear_B",
    "handempty",
    "holding_A",
]


#############
## ACTIONS ##
#############

actions = []
pre_p = {}
del_p = {}
add_p = {}

# A1-PICK-UP-A
actions.append("pick_up_A")
pre_p["pick_up_A"] = {"clear_A", "ontable_A", "handempty"}
del_p["pick_up_A"] = {"clear_A", "ontable_A", "handempty"}
add_p["pick_up_A"] = {"holding_A"}

# A2-STACK-A-B
actions.append("stack_A_B")
pre_p["stack_A_B"] = {"holding_A", "clear_B"}
del_p["stack_A_B"] = {"holding_A", "clear_B"}
add_p["stack_A_B"] = {"clear_A", "handempty", "on_A_B"}


#############
## PROBLEM ##
#############

I = [
    "clear_A",
    "clear_B",
    "ontable_A",
    "ontable_B",
    "handempty",
]

Gp = [
	"on_A_B"
]
