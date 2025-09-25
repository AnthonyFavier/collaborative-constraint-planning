#################
## PROBLEM INFO ##
##################

Vp = [
    "at_p1_loc1",
    "at_p1_loc2",
    "at_t1_loc1",
    "at_t1_loc2",
    "in_p1_t1",
]

I = [
    "at_p1_loc1",
    "at_t1_loc1",
]

Gp = [
	"at_p1_loc2"
]

actions = []
pre_p = {}
del_p = {}
add_p = {}

actions.append("load_p1_t1_loc1")
pre_p["load_p1_t1_loc1"] = {"at_p1_loc1", "at_t1_loc1"}
del_p["load_p1_t1_loc1"] = {"at_p1_loc1"}
add_p["load_p1_t1_loc1"] = {"in_p1_t1"}

actions.append("unload_p1_t1_loc2")
pre_p["unload_p1_t1_loc2"] = {"in_p1_t1", "at_t1_loc2"}
del_p["unload_p1_t1_loc2"] = {"in_p1_t1"}
add_p["unload_p1_t1_loc2"] = {"at_p1_loc2"}

actions.append("drive_t1_loc1_loc2")
pre_p["drive_t1_loc1_loc2"] = {"at_t1_loc1"}
del_p["drive_t1_loc1_loc2"] = {"at_t1_loc1"}
add_p["drive_t1_loc1_loc2"] = {"at_t1_loc2"}

