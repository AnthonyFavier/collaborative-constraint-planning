from pulp import *
from MILP.boxprint import boxprint
from MILP.convert_pddl import load_pddl
from datetime import datetime
import time
import click
import math
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus

##################
## LOAD PROBLEM ##
##################
def get_problem_filenames(domain_name, i_instance, classical=False):
    """
    ** Numerical ***
    block-grouping, counters, delivery, drone, expedition, ext-plant-watering, farmland, fo-counters, fo-farmland, fo-sailing, hydropower, markettrader, mprime, pathwaysmetric, rover, sailing, settlersnumeric, sugar, tpp, zenotravel

    ** Classical **
    agricola-opt18, caldera-sat18, elevators-00-adl, floortile-sat14-strips, maintenance-sat14-adl, openstacks, organic-synthesis-split-opt18, pegsol-sat11-strips, scanalyzer-08-strips, spider-sat18, transport-opt14-strips, woodworking-opt11-strips, agricola-sat18, caldera-split-opt18, elevators-00-full, freecell, miconic, openstacks-opt08-adl, organic-synthesis-split-sat18, petri-net-alignment-opt18, scanalyzer-opt11-strips, storage, transport-sat08-strips, woodworking-sat08-strips, airport, caldera-split-sat18, elevators-00-strips, fridge, miconic-fulladl, openstacks-opt08-strips, parcprinter-08-strips, petri-net-alignment-sat18, scanalyzer-sat11-strips, termes-opt18, transport-sat11-strips, woodworking-sat11-strips, airport-adl, cavediving, elevators-opt08-strips, ged-opt14-strips, miconic-simpleadl, openstacks-opt11-strips, parcprinter-opt11-strips, philosophers, schedule, termes-sat18, transport-sat14-strips, zenotravel, assembly, childsnack-opt14-strips, elevators-opt11-strips, ged-sat14-strips, movie, openstacks-opt14-strips, parcprinter-sat11-strips, pipesworld-06, settlers-opt18, tetris-opt14-strips, trucks, barman-opt11-strips, childsnack-sat14-strips, elevators-sat08-strips, grid, mprime, openstacks-sat08-adl, parking-opt11-strips, pipesworld-notankage, settlers-sat18, tetris-sat14-strips, trucks-strips, barman-opt14-strips, citycar-opt14-adl, elevators-sat11-strips, gripper, mystery, openstacks-sat08-strips, parking-opt14-strips, pipesworld-tankage, snake-opt18, thoughtful-sat14-strips, tsp, barman-sat11-strips, citycar-sat14-adl, ferry, hanoi, no-mprime, openstacks-sat11-strips, parking-sat11-strips, psr-large, snake-sat18, tidybot-opt11-strips, tyreworld, barman-sat14-strips, cybersec, flashfill-opt18, hiking-opt14-strips, no-mystery, openstacks-sat14-strips, parking-sat14-strips, psr-middle, sokoban-opt08-strips, tidybot-opt14-strips, visitall-opt11-strips, blocks, data-network-opt18, flashfill-sat18, hiking-sat14-strips, nomystery-opt11-strips, openstacks-strips, pathways, psr-small, sokoban-opt11-strips, tidybot-sat11-strips, visitall-opt14-strips, blocks-3op, data-network-sat18, floortile-opt11-strips, logistics00, nomystery-sat11-strips, optical-telegraphs, pathways-noneg, rovers, sokoban-sat08-strips, tpp, visitall-sat11-strips, briefcaseworld, depot, floortile-opt14-strips, logistics98, nurikabe-opt18, organic-synthesis-opt18, pegsol-08-strips, rovers-02, sokoban-sat11-strips, transport-opt08-strips, visitall-sat14-strips, caldera-opt18, driverlog, floortile-sat11-strips, maintenance-opt14-adl, nurikabe-sat18, organic-synthesis-sat18, pegsol-opt11-strips, satellite, spider-opt18, transport-opt11-strips, woodworking-opt08-strips
    """

    if classical:

        if domain_name == 'airport':
            problems = [('airport/p01-domain.pddl', 'airport/p01-airport1-p1.pddl'),
                ('airport/p02-domain.pddl', 'airport/p02-airport1-p1.pddl'),
                ('airport/p03-domain.pddl', 'airport/p03-airport1-p2.pddl'),
                ('airport/p04-domain.pddl', 'airport/p04-airport2-p1.pddl'),
                ('airport/p05-domain.pddl', 'airport/p05-airport2-p1.pddl'),
                ('airport/p06-domain.pddl', 'airport/p06-airport2-p2.pddl'),
                ('airport/p07-domain.pddl', 'airport/p07-airport2-p2.pddl'),
                ('airport/p08-domain.pddl', 'airport/p08-airport2-p3.pddl'),
                ('airport/p09-domain.pddl', 'airport/p09-airport2-p4.pddl'),
                ('airport/p10-domain.pddl', 'airport/p10-airport3-p1.pddl'),
                ('airport/p11-domain.pddl', 'airport/p11-airport3-p1.pddl'),
                ('airport/p12-domain.pddl', 'airport/p12-airport3-p2.pddl'),
                ('airport/p13-domain.pddl', 'airport/p13-airport3-p2.pddl'),
                ('airport/p14-domain.pddl', 'airport/p14-airport3-p3.pddl'),
                ('airport/p15-domain.pddl', 'airport/p15-airport3-p3.pddl'),
                ('airport/p16-domain.pddl', 'airport/p16-airport3-p4.pddl'),
                ('airport/p17-domain.pddl', 'airport/p17-airport3-p5.pddl'),
                ('airport/p18-domain.pddl', 'airport/p18-airport3-p6.pddl'),
                ('airport/p19-domain.pddl', 'airport/p19-airport3-p6.pddl'),
                ('airport/p20-domain.pddl', 'airport/p20-airport3-p7.pddl'),
                ('airport/p21-domain.pddl',
                'airport/p21-airport4halfMUC-p2.pddl'),
                ('airport/p22-domain.pddl',
                'airport/p22-airport4halfMUC-p3.pddl'),
                ('airport/p23-domain.pddl',
                'airport/p23-airport4halfMUC-p4.pddl'),
                ('airport/p24-domain.pddl',
                'airport/p24-airport4halfMUC-p4.pddl'),
                ('airport/p25-domain.pddl',
                'airport/p25-airport4halfMUC-p5.pddl'),
                ('airport/p26-domain.pddl',
                'airport/p26-airport4halfMUC-p6.pddl'),
                ('airport/p27-domain.pddl',
                'airport/p27-airport4halfMUC-p6.pddl'),
                ('airport/p28-domain.pddl',
                'airport/p28-airport4halfMUC-p7.pddl'),
                ('airport/p29-domain.pddl',
                'airport/p29-airport4halfMUC-p8.pddl'),
                ('airport/p30-domain.pddl',
                'airport/p30-airport4halfMUC-p8.pddl'),
                ('airport/p31-domain.pddl',
                'airport/p31-airport4halfMUC-p9.pddl'),
                ('airport/p32-domain.pddl',
                'airport/p32-airport4halfMUC-p10.pddl'),
                ('airport/p33-domain.pddl',
                'airport/p33-airport4halfMUC-p10.pddl'),
                ('airport/p34-domain.pddl',
                'airport/p34-airport4halfMUC-p11.pddl'),
                ('airport/p35-domain.pddl',
                'airport/p35-airport4halfMUC-p12.pddl'),
                ('airport/p36-domain.pddl', 'airport/p36-airport5MUC-p2.pddl'),
                ('airport/p37-domain.pddl', 'airport/p37-airport5MUC-p3.pddl'),
                ('airport/p38-domain.pddl', 'airport/p38-airport5MUC-p3.pddl'),
                ('airport/p39-domain.pddl', 'airport/p39-airport5MUC-p4.pddl'),
                ('airport/p40-domain.pddl', 'airport/p40-airport5MUC-p4.pddl'),
                ('airport/p41-domain.pddl', 'airport/p41-airport5MUC-p4.pddl'),
                ('airport/p42-domain.pddl', 'airport/p42-airport5MUC-p5.pddl'),
                ('airport/p43-domain.pddl', 'airport/p43-airport5MUC-p5.pddl'),
                ('airport/p44-domain.pddl', 'airport/p44-airport5MUC-p5.pddl'),
                ('airport/p45-domain.pddl', 'airport/p45-airport5MUC-p6.pddl'),
                ('airport/p46-domain.pddl', 'airport/p46-airport5MUC-p6.pddl'),
                ('airport/p47-domain.pddl', 'airport/p47-airport5MUC-p8.pddl'),
                ('airport/p48-domain.pddl', 'airport/p48-airport5MUC-p9.pddl'),
                ('airport/p49-domain.pddl', 'airport/p49-airport5MUC-p10.pddl'),
                ('airport/p50-domain.pddl', 'airport/p50-airport5MUC-p15.pddl')]
            domain_filename = f'classical-domains/classical/' + problems[i_instance][0]
            problem_filename = f'classical-domains/classical/' + problems[i_instance][1]

        elif domain_name=='blocks':
            problems = [('blocks/domain.pddl', 'blocks/probBLOCKS-10-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-10-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-10-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-11-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-11-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-11-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-12-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-12-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-13-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-13-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-14-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-14-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-15-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-15-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-16-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-16-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-17-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-17-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-18-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-18-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-19-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-19-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-20-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-20-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-25-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-25-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-28-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-28-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-30-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-30-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-35-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-35-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-4-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-4-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-4-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-40-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-40-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-45-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-45-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-5-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-5-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-5-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-50-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-50-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-55-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-55-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-6-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-6-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-6-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-60-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-60-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-7-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-7-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-7-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-8-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-8-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-8-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-9-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-9-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-9-2.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-100-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-100-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-200-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-200-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-250-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-250-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-300-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-300-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-350-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-350-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-400-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-400-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-425-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-425-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-450-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-450-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-475-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-475-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-500-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-500-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-65-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-65-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-70-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-70-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-80-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-80-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-90-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-90-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-95-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probblocks-95-1.pddl'),
              #
              # Newly added
              ('blocks/domain.pddl', 'blocks/probBLOCKS-21-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-21-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-22-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-22-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-23-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-23-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-24-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-24-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-26-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-26-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-27-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-27-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-29-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-29-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-31-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-31-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-32-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-32-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-33-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-33-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-34-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-34-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-36-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-36-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-37-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-37-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-38-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-38-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-39-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-39-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-41-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-41-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-42-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-42-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-43-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-43-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-44-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-44-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-46-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-46-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-47-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-47-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-48-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-48-1.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-49-0.pddl'),
              ('blocks/domain.pddl', 'blocks/probBLOCKS-49-1.pddl')]
            domain_filename = f'classical-domains/classical/' + problems[i_instance][0]
            problem_filename = f'classical-domains/classical/' + problems[i_instance][1]

        elif domain_name=='childsnack':
            problems = [('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile01-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile01.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile02-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile02.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile03-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile03.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile04-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile04.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile05-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile05.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile06-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile06.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile07-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile07.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile08-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile08.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile09-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile09.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile10-2.pddl'),
              ('childsnack-opt14-strips/domain.pddl',
               'childsnack-opt14-strips/child-snack_pfile10.pddl')]
            domain_filename = f'classical-domains/classical/' + problems[i_instance][0]
            problem_filename = f'classical-domains/classical/' + problems[i_instance][1]

        else:
            domain_filename = f'classical-domains/classical/{domain_name}/domain.pddl'  
            problem_filename = f'classical-domains/classical/{domain_name}/pfile{i_instance}.pddl'

    else:
        domain_filename = f'ipc2023-dataset/{domain_name}/domain.pddl'  
        problem_filename = f'ipc2023-dataset/{domain_name}/instances/pfile{i_instance}.pddl'

    return domain_filename, problem_filename

class MILP_data_extracted:
    def __init__(self, data_extracted):
        V, actions, I, G, num_param, actionsAffectingF = data_extracted
        Vp, Vn = V # Fluents
        Gp, Gn = G # Goal state
        w_c_v, w_0_c, k_v_a_w, k_v_a = num_param # Parameters describing numerical preconditions, goals, and effects
        pref, addf, delf, se, le = actionsAffectingF # Actions affecting given fluent

        self.actions = actions
        self.Vp = Vp
        self.Vn = Vn
        self.I = I
        self.Gp = Gp
        self.Gn = Gn
        self.w_c_v = w_c_v
        self.w_0_c = w_0_c
        self.k_v_a_w = k_v_a_w
        self.k_v_a = k_v_a
        self.pref = pref
        self.addf = addf
        self.delf = delf
        self.se = se
        self.le = le

#################
## BUILD MODEL ##
#################
def compute_m_constants(M: MILP_data_extracted, T):

    # compute m_v_t, M_v_t
    global M_v_t, m_v_t
    m_v_t = {}
    M_v_t = {}
    for v in M.Vn:
        m_v_t[v] = {}
        M_v_t[v] = {}
        for t in range(0, T+1):
            if t==0:
                m_v_t[v][t] = M.I[v]
                M_v_t[v][t] = M.I[v]

            else:
                min_a_bot = min(
                    sum(M.k_v_a_w[v][a][w] * m_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] > 0)\
                    + sum(M.k_v_a_w[v][a][w] * M_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] < 0)\
                    for a in M.le[v]
                ) if M.le[v] else math.inf

                max_a_top = max(
                    sum(M.k_v_a_w[v][a][w] * M_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] > 0) \
                    + sum(M.k_v_a_w[v][a][w] * m_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] < 0)\
                    for a in M.le[v]
                ) if M.le[v] else -math.inf

                m_v_t[v][t] = min(
                    m_v_t[v][t-1] + sum(M.k_v_a[v][a] for a in M.se[v] if M.k_v_a[v][a] < 0),
                    min_a_bot
                )
 
                M_v_t[v][t] = max(
                    M_v_t[v][t-1] + sum(M.k_v_a[v][a] for a in M.se[v] if M.k_v_a[v][a] > 0),
                    max_a_top
                )

    # Compute m_c_t
    m_c_t = {}
    for a in M.actions:
        for c in M.actions[a]['pre_n']:
            m_c_t[c] = {}
            for t in range(0, T):
                m_c_t[c][t] = sum(M.w_c_v[c][v] * M_v_t[v][t] for v in M.Vn if M.w_c_v[c][v]<0)\
                + sum(M.w_c_v[c][v] * m_v_t[v][t] for v in M.Vn if M.w_c_v[c][v]>0)\
                + M.w_0_c[c]

    # Compute m/M_step_c_t
    M_step_v_t = {}
    m_step_v_t = {}
    for v in M.Vn:
        M_step_v_t[v] = {}
        m_step_v_t[v] = {}
        for t in range(0, T+1):
            if t==0:
                M_step_v_t[v][t] = M_v_t[v][t]
                m_step_v_t[v][t] = m_v_t[v][t]
            else:
                M_step_v_t[v][t] = M_v_t[v][t] - m_v_t[v][t-1]
                m_step_v_t[v][t] = m_v_t[v][t] - M_v_t[v][t-1]

    # Compute m/M_v_a_t
    M_v_a_t = {}
    m_v_a_t = {}
    for v in M.Vn:
        M_v_a_t[v] = {}
        m_v_a_t[v] = {}
        for a in M.le[v]:
            M_v_a_t[v][a] = {}
            m_v_a_t[v][a] = {}
            for t in range(0, T+1):
                if t==0:
                    M_v_a_t[v][a][t] = M_v_t[v][t]
                    m_v_a_t[v][a][t] = m_v_t[v][t]
                else:
                    M_v_a_t[v][a][t] = M_v_t[v][t]\
                    - sum(M.k_v_a_w[v][a][w] * M_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]<0)\
                    + sum(M.k_v_a_w[v][a][w] * m_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]>0)\
                    - M.k_v_a[v][a]
                    
                    m_v_a_t[v][a][t] = m_v_t[v][t]\
                    - sum(M.k_v_a_w[v][a][w] * M_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]>0)\
                    + sum(M.k_v_a_w[v][a][w] * m_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]<0)\
                    - M.k_v_a[v][a]

    return m_c_t, m_step_v_t, M_step_v_t, m_v_a_t, M_v_a_t

def build_nmutex(M: MILP_data_extracted):
    def are_nmutex(a1, a2):
        if a1 != a2:
            for e1 in M.actions[a1]['num']:
                v = e1.split(':=')[0].strip()

                # check (i): v is assigned by a1 and is also used in one of the numeric effects of a2
                for e2 in M.actions[a2]['num']:
                    # if v in e2: 
                        # return True

                    # paper exact below
                    xi = e2.split(':=')[1].strip()
                    if v in xi:
                        return True

                # check (ii): v is assigned by a1 and is also part of a precondition of a2
                for pre in M.actions[a2]['pre_n']:
                    # if v in pre:
                    #     return True

                    # paper exact below
                    if M.w_c_v[pre][v]!=0:
                        return True

        return False

    nmutex = {}
    for a1 in M.actions:
        nmutex[a1] = set()
        for a2 in M.actions:
            if are_nmutex(a1, a2):
                nmutex[a1].add(a2)

    return nmutex

def get_op(c):
    rel_ops = ['>=', '>', '==', None]
    for op in rel_ops:
        if op in c:
            break
    assert op != None
    return op
                
def build_model_piacentini2018_state_change_numeric(M: MILP_data_extracted, T, sequential):
    global u

    m_c_t, m_step_v_t, M_step_v_t, m_v_a_t, M_v_a_t = compute_m_constants(M, T)
    nmutex = build_nmutex(M)

    t1 = time.time()
    print('Building model...')

    ###########
    ## MODEL ##
    ###########
    m = LpProblem(sense=LpMinimize)
 
    ###############
    ## VARIABLES ##
    ###############
    # Action variables
    u = {}
    for a in M.actions:
        u[a] = {}
        for t in range(0, T):
            u[a][t] = LpVariable(f'u_{a}_{t}', cat='Binary') # True if action a is executed at time step t
            
    # Propositional fluent state change variables
    u_m = {} 
    u_pa = {}
    u_pd = {}
    u_a = {}
    for p in M.Vp:
        u_m[p] = {}
        u_pa[p] = {}
        u_pd[p] = {}
        u_a[p] = {}
        for t in range(0, T+1):
            u_m[p][t] = LpVariable(f'u_m_{p}_{t}', cat='Binary') # True if fluent is propagated (noop)
            u_pa[p][t] = LpVariable(f'u_pa_{p}_{t}', cat='Binary') # True if an action is executed at t and has f as precondition and doesn't delete it (maintainted/propagated)
            u_pd[p][t] = LpVariable(f'u_pd_{p}_{t}', cat='Binary') # True if an action is executed at t and has f as precondition and delete effect
            u_a[p][t] = LpVariable(f'u_a_{p}_{t}', cat='Binary') # True if an action is executed at t and has f in add effect but not in precondition
    
    # Numeric fluent value variables
    y_v_t = {}
    for v in M.Vn:
        y_v_t[v] = {}
        for t in range(0, T+1):
            y_v_t[v][t] = LpVariable(f'y_v_t_{v}_{t}', cat='Continuous') # value of fluent v at time step t
            

    ###############
    ## OBJECTIVE ##
    ###############
    def obj_nb_actions(m):
        L = []
        for a in M.actions:
            for t in range(0, T):
                cost_a = 1
                L.append(cost_a * u[a][t])
        m += lpSum(L)
    obj_nb_actions(m)
        
        
    ###############################
    ## CONSTRAINTS PROPOSITIONAL ##
    ###############################
    
    # Initial State
    for p in M.Vp:
        m += u_a[p][0] == M.I[p] #(1)
        m += u_m[p][0] == 0 
        m += u_pa[p][0] == 0 
        m += u_pd[p][0] == 0 
        
    # Goal State
    for p in M.Gp:
        m += u_a[p][T] + u_pa[p][T] + u_m[p][T] >= 1 #(2)
    
    for p in M.Vp:
        for t in range(0, T):
            m += lpSum(u[a][t] for a in M.pref[p].difference(M.delf[p])) >= u_pa[p][t+1] #(3)
            for a in M.pref[p].difference(M.delf[p]):
                m += u[a][t] <= u_pa[p][t+1] #(6)

            m += lpSum(u[a][t] for a in M.addf[p].difference(M.pref[p])) >= u_a[p][t+1] #(4)
            for a in M.addf[p].difference(M.pref[p]):
                m += u[a][t] <= u_a[p][t+1] #(7)
                
            m += lpSum(u[a][t] for a in M.pref[p].intersection(M.delf[p])) == u_pd[p][t+1] #(5)
            
            m += u_pa[p][t+1] + u_m[p][t+1] + u_pd[p][t+1] <= u_a[p][t] + u_pa[p][t] + u_m[p][t] #(11)
            
        for t in range(0, T+1):
            m += u_a[p][t] + u_m[p][t] + u_pd[p][t] <= 1 #(8)
            m += u_pa[p][t] + u_m[p][t] + u_pd[p][t] <= 1 #(9)

    # Add (10) back?
    for a1_name in M.actions:
        for a2_name in M.actions:
            if a1_name!=a2_name:
                a1 = M.actions[a1_name]
                a2 = M.actions[a2_name]
                # set operators: | union, & intersection, - difference
                if a1['del'] & (a2['add'] | a2['pre_p']) != set():
                    for t in range(0, T):
                        u[a1_name][t] + u[a2_name][t] <= 1

    #########################
    ## CONSTRAINTS NUMERIC ##
    #########################

    for v in M.Vn:
        m += y_v_t[v][0] == M.I[v] #(12)
    
    for c in M.Gn: #(13)
        op = get_op(c)
        if op=='>=':
            m += lpSum(M.w_c_v[c][v] * y_v_t[v][T] for v in M.Vn) + M.w_0_c[c] >= 0
        elif op=='==':
            m += lpSum(M.w_c_v[c][v] * y_v_t[v][T] for v in M.Vn) + M.w_0_c[c] == 0
        else:
            raise Exception('Numeric goal constraint: op not supported')

    for a in M.actions: #(14)
        for c in M.actions[a]['pre_n']:
            for t in range(0, T):
                op = get_op(c)
                if op=='>=':
                    m += sum(M.w_c_v[c][v] * y_v_t[v][t] for v in M.Vn) + M.w_0_c[c] >= m_c_t[c][t]*(1-u[a][t])
                if op=='==':
                    m += sum(M.w_c_v[c][v] * y_v_t[v][t] for v in M.Vn) + M.w_0_c[c] == m_c_t[c][t]*(1-u[a][t])

    for v in M.Vn: #(15)
        for t in range(0, T):
            m += y_v_t[v][t+1] <= y_v_t[v][t]\
            + sum(M.k_v_a[v][a] * u[a][t] for a in M.se[v])\
            + M_step_v_t[v][t+1] * sum(u[a][t] for a in M.le[v])

    for v in M.Vn: #(16)
        for t in range(0, T):
            m += y_v_t[v][t+1] >= y_v_t[v][t]\
            + sum(M.k_v_a[v][a] * u[a][t] for a in M.se[v])\
            + m_step_v_t[v][t+1] * sum(u[a][t] for a in M.le[v])

    for v in M.Vn: #(17)
        for a in M.le[v]:
            for t in range(0, T):
                m += y_v_t[v][t+1] - sum(M.k_v_a_w[v][a][w] * y_v_t[w][t] for w in M.Vn) <=\
                M.k_v_a[v][a] + M_v_a_t[v][a][t+1] * (1-u[a][t])

    for v in M.Vn: #(18)
        for a in M.le[v]:
            for t in range(0, T):
                m += y_v_t[v][t+1] - sum(M.k_v_a_w[v][a][w] * y_v_t[w][t] for w in M.Vn) >=\
                M.k_v_a[v][a] + m_v_a_t[v][a][t+1] * (1-u[a][t])

    for a1 in M.actions: #(19)
        for a2 in nmutex[a1]:
            for t in range(0, T):
                m += u[a1][t] + u[a2][t] <= 1


    ############################
    ## ADDITIONAL CONSTRAINTS ##
    ############################

    # (own)
    if sequential:
        for t in range (0, T):
            m += lpSum(u[a][t] for a in M.actions) <= 1


    # No zoom
    # for a in M.actions:
    #     for t in range(0, T):
    #         action_lifted = a.split('_')[0]
    #         if action_lifted=='zoom':
    #             m += u[a][t] == 0

    # def get_unwanted_fluents(person, c1, c2):
    #     cities = [f'city{i}' for i in range(0, 5)]

    #     unwanted_fluents = []
    #     for c in cities:
    #         if c not in [c1, c2]:
    #             unwanted_fluents.append(f'at__{person}_{c}')

    #     return unwanted_fluents
    # persons_cities = [
    #     ('person1', 'city3', 'city1'),
    #     ('person2', 'city3', 'city2'),
    #     ('person3', 'city4', 'city3'),
    #     ('person4', 'city4', 'city1'),
    #     ('person5', 'city1', 'city0'),
    #     ('person6', 'city0', 'city3'),
    #     ('person7', 'city1', 'city4'),
    #     ('person8', 'city0', 'city3'),
    # ]

    # unwanted_fluents = []
    # for pc in persons_cities:
    #     p, c1, c2 = pc
    #     unwanted_fluents += get_unwanted_fluents(p, c1, c2)

    # print('Unwanted fluents:\n' + '\n'.join(unwanted_fluents))

    # for p in unwanted_fluents:
    #     for t in range(0, T+1):
    #         m += u_m[p][t] == 0
    #         m += u_pa[p][t] == 0
    #         m += u_pd[p][t] == 0
    #         m += u_a[p][t] == 0

    #########################
    
    global g_building_model_time
    g_building_model_time = time.time()-t1
    print(f"[Building Model: {g_building_model_time:.2f}s]")
    return m      


#############
## SOLVING ##
#############
def solve(m, sol_gap, solver_name="PULP_CBC_CMD"):
    if sol_gap!=None:
        sol_gap = float(sol_gap)
    
    print(f'[{datetime.now()}] Start solving ... ')
    solver = getSolver(solver_name, gapRel=sol_gap)
    t1 = time.time()
    m.solve(solver=solver)

    global g_solving_time
    g_solving_time = time.time()-t1
    print(f'elapsed: {g_solving_time:.2f}s')
    

######################
## EXTRACT SOLUTION ##
######################
def extract_solution(domain_filename, problem_filename, m, time_horizon):

    boxprint(f'{domain_filename}\n{problem_filename}\nNb Constraints: {m.numConstraints()}\nNb Variables: {m.numVariables()}')

    boxprint(f'Time horizon: {time_horizon}')

    if m.status!=1:
        boxprint(f'Problem: {LpStatus[m.status]}', mode='d')
    else:
        boxprint(LpSolution[m.sol_status])
        
        plan = {}
        print("plan:")
        # for t in range(1, time_horizon+1): # for vossen
        for t in range(0, time_horizon): # for piacentini
            time_stamp_txt = f'{t}: '
            print(time_stamp_txt, end='')
            for a in u:
                if t not in plan:
                    plan[t] = []
                    
                if u[a][t].value():
                    spaces = '' if len(plan[t])==0 else ' '*(len(time_stamp_txt))
                    
                    action_name = str(u[a][t])
                    action_name = action_name[action_name.find('_')+1:action_name.rfind('_')]
                        
                    plan[t].append( action_name )
                    
                    print(f'{spaces}{action_name}')
                    
            if plan[t] == []:
                print('<noop>')

    return plan


##############
## UP SOLVE ##
##############
def up_solve(domain_name=None, i_instance=None, domain_filename=None, problem_filename=None, classical=False):
    t_total_1 = time.time()

    if domain_name!=None and i_instance!=None:
        domain_filename, problem_filename = get_problem_filenames(domain_name, i_instance, classical=classical)
    problem_name, up_problem, milp_problem = load_pddl(domain_filename, problem_filename, no_data_extraction=True)

    boxprint(f"UP Solving")

    t_solving_1 = time.time()
    with OneshotPlanner(problem_kind=up_problem.kind, 
        optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY
    ) as planner:
        result = planner.solve(up_problem)
        up_solving_time = time.time()-t_solving_1
        plan_str = []
        for t, a in enumerate(str(result.plan).splitlines()[1:]):
            a = a.strip().replace('(','_').replace(')','').replace(', ','_')
            plan_str.append(f'{t}: {a}')
        plan_str = ' | '.join(plan_str)
        plan_length = len(result.plan.actions)

    total_time = time.time()-t_total_1

    from MILP.convert_pddl import g_loading_problem_time
    return plan_str, plan_length, (g_loading_problem_time, up_solving_time, total_time)

########################################################

##########
## MAIN ##
##########
@click.command()
@click.option('--tmin', 'T_min', default=1)
@click.option('--tmax', 'T_max', default=200)
@click.option('-t', '--timehorizon', 'T_user', default=None)
@click.option('--gap', 'sol_gap', default=None)
@click.option('--seq', 'sequential', is_flag=True, default=False)
@click.option('--domain_name', 'domain_name', default=None)
@click.option('--i_instance', 'i_instance', default=None)
@click.option('--domain_filename', 'domain_filename', default=None)
@click.option('--problem_filename', 'problem_filename', default=None)
def mainCLI(T_min, T_max, T_user, sol_gap, sequential, domain_name, i_instance, domain_filename, problem_filename):
    main(T_min, T_max, T_user, sol_gap, sequential, domain_name, i_instance, domain_filename, problem_filename)
def main(T_min, T_max, T_user, sol_gap, sequential, domain_name, i_instance, domain_filename, problem_filename):
    t_start = time.time()

    if domain_name==None and i_instance==None and \
    domain_filename==None and problem_filename==None:
        print('ERROR: no problem given.\nSpecify either (domain_name, i_instance) or (domain_filename, problem_filename).')
        return -1


    if domain_name!=None and i_instance!=None:
        domain_filename, problem_filename = get_problem_filenames(domain_name, i_instance)
    
    problem_name, up_problem, data_extracted = load_pddl(domain_filename, problem_filename)
    milp_data_problem = MILP_data_extracted(data_extracted)
    
    if T_user!=None:
        T_min = T_max = int(T_user)
    
    solved = False
    T = T_min
    while not solved and T<=T_max:
        boxprint(f"Solving with T={T}")
        
        m = build_model_piacentini2018_state_change_numeric(milp_data_problem, T, sequential)

        # with open('ip_model.txt', 'w') as f:
        #     f.write(str(m))

        solve(m, sol_gap, solver_name='GUROBI') # solvers: CPLEX_PY, GUROBI, PULP_CBC_CMD
        
        with open('output.txt', 'w') as f:
            txt = ''
            txt += 'Constraints:\n'
            for k,c in m.constraints.items():
                txt += f'{k} = {c}\n'
            txt += '\nVariables:\n'
            for v in m._variables:
                txt += f'{v} = {v.varValue}\n'
            f.write(txt)
            
        if m.status==1:
            solved=True
            global g_total_solving_time
            g_total_solving_time = time.time()-t_start
        elif T==T_max:
            if T_user!=None:
                raise Exception(f"No solution found for time horizon ({T_user}).")
                break
            else:
                raise Exception(f"Max time horizon ({T_max}) reached.")
        else: 
            T+=1
            
    plan = extract_solution(domain_filename, problem_filename, m, T)

    from MILP.convert_pddl import g_loading_problem_time

    # show times
    boxprint(f'\
Loading problem: {g_loading_problem_time:.2f}s\n\
Building model: {g_building_model_time:.2f}s\n\
Solving instance: {g_solving_time:.2f}s\n\
Total time: {g_total_solving_time:.2f}s\
')
    

    plan_length = 0
    plan_str = []
    for t in plan:
        plan_length += len(plan[t])
        plan_str.append(f'{t}: ' + ', '.join(plan[t]))
    plan_str = ' | '.join(plan_str)

    return plan_str, plan_length, (g_loading_problem_time, g_building_model_time, g_solving_time, g_total_solving_time)

if __name__=='__main__':
    mainCLI()