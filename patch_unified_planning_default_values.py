
import sys
path = "env_cai/lib/python3.10/site-packages/unified_planning/io/pddl_reader.py"

with open(path, 'r') as f:
    txt = f.read()

to_insert = ",self._tm.IntType(): self._em.Int(0),self._tm.RealType(): self._em.Real(Fraction())"

if len(sys.argv)<2 or sys.argv[1] != "undo":
    if txt.find("initial_defaults={self._tm.BoolType(): self._em.FALSE()" + to_insert + "},")!=-1:
        print("Already patched")
        exit()

    t = "problem = up.model.Problem("
    i = txt.find(t)
    if i==-1:
        raise Exception("Can't find right place to edit")
    i+=len(t)

    t="initial_defaults={self._tm.BoolType(): self._em.FALSE()"
    i = txt.find(t, i)
    if i==-1:
        raise Exception("Can't find right place to edit")
    i+=len(t)

    txt = txt[:i] + to_insert + txt[i:]

    with open(path, 'w') as f:
        f.write(txt)
        
    print("patch done!")
    
###############################################################
    
elif sys.argv[1] == "undo":
    i = txt.find(to_insert)
    if i==-1:
        print("not patched")
        exit()
    
    txt = txt[:i] + txt[i+len(to_insert):]
    
    with open(path, 'w') as f:
        f.write(txt)
    print("unpatched!")    
