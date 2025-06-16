import json
import sys
import click
import numpy


@click.command()
@click.argument('filename')
def main(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
        
    # print(data)
    
    # Get best metric
    tests = data['tests']
    
    successful = []
    for t in tests:
        if t['result']=='success':
            successful.append(t)
            
    metrics = numpy.array([t['metric'] for t in successful])
    mean = metrics.mean()
    std = metrics.std()
    min_metric = metrics.min()
    
    constraints = [t['constraint'] for t in tests]
    my_dict = {x:constraints.count(x) for x in constraints}
    
    print("repeated constraints:")
    repeated = 0
    for k,n in my_dict.items():
        if n>1:
            print(f'\t{n}: {k}')
            repeated+=1
    
    print(f"Success = {100*len(successful)/len(tests):.1f}%")
    print(f"Repeated = {100*repeated/len(tests):.1f}%")
    print(f"Metric = {mean:.1f} +- {std:.1f}")
    print(f"Best = {min_metric:.1f}")
    
    


if __name__=='__main__':
    sys.argv += ['50-200-TO5_06-16-2025_10:07:57.json']
    main()