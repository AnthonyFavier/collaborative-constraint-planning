from unified_planning.io import PDDLReader, PDDLWriter
from NumericTCORE.bin.ntcore import main as ntcore
from defs import *

dp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl'
pp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl'


dp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl'
pp = '/home/afavier/CAI/tmp/test.pddl'

print("Parsing:")
reader = PDDLReader()
pddl_problem = reader.parse_problem(dp, pp)
print(pddl_problem)

# exit()

print("Compiling:")
ntcore(dp, pp, "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
print("Compiled")
