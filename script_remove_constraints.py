
for i in range(1,23):
    with open(f'/home/afavier/NeedAGoodName/NumericTCORE/benchmark/ZenoTravel/pfile{i}.pddl', 'r+') as f:
        data = f.read()
        
        i_s = data.find('(:constraints')
        
        if i_s!=-1:
            nb = 1
            i = i_s + 1
            while nb!=0:
                if data[i]=='(':
                    nb+=1
                if data[i]==')':
                    nb-=1
                i+=1
                
            data = data[:i_s] + data[i:]
            
            f.seek(0)
            f.write(data)
            f.truncate()
        