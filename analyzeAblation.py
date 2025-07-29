from scipy.stats import shapiro, wilcoxon, mannwhitneyu
import csv

def extractCSV(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = {
            'encoding':[],
            'parsable':[],
            'input_time':[],
            'interaction_time':[],
            'decomp_time':[],
            'encoding_time':[],
            'translation_time':[],
            'correctness':[],
            'h_review':[],
            'h_intervention':[],
            'comment':[],
        }
        for row in reader:
            for i,k in enumerate(data):
                d = row[i] if k in ['encoding', 'comment'] else float(row[i])
                data[k].append(d)
                
        return data

data = {
    'DIRECT': extractCSV('/home/afavier/ws/CAI/export results for ablation/1-DIRECT/DIRECT.csv'),
    'VERIFIER': extractCSV('/home/afavier/ws/CAI/export results for ablation/3-VERIFIER/VERIFIER.csv'),
    'DECOMP': extractCSV('/home/afavier/ws/CAI/export results for ablation/4-DECOMP/DECOMP.csv'),
    'DECOMP_CONFIRM': extractCSV('/home/afavier/ws/CAI/export results for ablation/5-DECOMP_CONFIRM/DECOMP_CONFIRM.csv'),
}



import numpy as np
from scipy.stats import bartlett
from scipy.stats import levene
from scipy.stats import normaltest



# Homogeneity
def testHomogeneity(set1, set2, var):
    print('')

    ## Bartlett's Test
    print(f"Bartlett: {set1}-{set2} {var}")
    r = bartlett(data[set1][var], data[set2][var])
    if r[1] < 0.05:
        print('Reject the null hypothesis of equal variance between groups. (Unequal Variance)')
        print(f'P-value is {r[1]}.')
    else:
        print('Fail to reject the null hypothesis of equal variance between groups. (suggest Equal Variance)')
        print(f'P-value is {r[1]}.')

    ## Levene's Test
    print(f"Levene: {set1}-{set2} {var}")
    r = levene(data[set1][var], data[set2][var])
    if r[1] < 0.05:
        print('Reject the null hypothesis of equal variance between groups. (Unequal Variance)')
        print(f'P-value is {r[1]}.')
    else:
        print('Fail to reject the null hypothesis of equal variance between groups. (suggest Equal Variance)')
        print(f'P-value is {r[1]}.')

testHomogeneity('DIRECT', 'VERIFIER', 'parsable')
testHomogeneity('DIRECT', 'VERIFIER', 'correctness')
testHomogeneity('DECOMP', 'DECOMP_CONFIRM', 'correctness')

# Normality

def testNormality(set, var):
    print('')
    print(f"Normal: {set} {var}")
    r = normaltest(data[set][var])
    if r[1] < 0.05:
        print('Reject the null hypothesis of normal distribution. (No normal distribution)')
        print(f'P-value is {r[1]}.')
    else:
        print('Fail to reject the null hypothesis of normal distribution. (suggest normal distribution)')
        print(f'P-value is {r[1]}.')

testNormality('DIRECT', 'parsable')
testNormality('VERIFIER', 'parsable')
testNormality('DECOMP', 'correctness')
testNormality('DECOMP_CONFIRM', 'correctness')

from scipy.stats import describe, ranksums

print('  ')
print(describe(data['DIRECT']['correctness']))
print(describe(data['DECOMP_CONFIRM']['correctness']))
testHomogeneity('DIRECT', 'DECOMP_CONFIRM', 'correctness')
testNormality('DIRECT', 'correctness')
testNormality('DECOMP_CONFIRM', 'correctness')
print(ranksums(data['DIRECT']['correctness'], data['DECOMP_CONFIRM']['correctness']))