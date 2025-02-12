
import pathlib
path = str(pathlib.Path().resolve())+'/'

for i in range(1,24):
    with open(f'{path}NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile{i}.pddl', 'r+') as f:
        data = f.read()
        
        i_s_m = data.find('(:constraints')
        if i_s_m!=-1:
            nb = 1
            i = i_s_m + 1
            while nb!=0:
                if data[i]=='(':
                    nb+=1
                if data[i]==')':
                    nb-=1
                i+=1
            data = data[:i_s_m] + data[i:]
            
        i_s_c = data.find('(:metric')
        if i_s_c!=-1:
            nb = 1
            i = i_s_c + 1
            while nb!=0:
                if data[i]=='(':
                    nb+=1
                if data[i]==')':
                    nb-=1
                i+=1
            data = data[:i_s_c] + data[i:]
            
        if i_s_m!=-1 or i_s_c!=-1:
            f.seek(0)
            f.write(data)
            f.truncate()
        