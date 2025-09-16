from scipy.stats import shapiro, wilcoxon, mannwhitneyu
import csv

import numpy as np
from scipy.stats import bartlett
from scipy.stats import levene
from scipy.stats import normaltest

from scipy.stats import describe, ranksums, fisher_exact
from scipy.stats import hypergeom
from statsmodels.stats.proportion import proportions_ztest


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

# Homogeneity
def testHomogeneity(set1, set2, var):
    print('')

    # ## Bartlett's Test
    # print(f"Homogeneity (Bartlett): {set1}-{set2} {var}")
    # r = bartlett(data[set1][var], data[set2][var])
    # if r[1] < 0.05:
    #     print('Reject the null hypothesis of equal variance between groups. (Unequal Variance)')
    #     print(f'P-value is {r[1]}.')
    # else:
    #     print('Fail to reject the null hypothesis of equal variance between groups. (suggest Equal Variance)')
    #     print(f'P-value is {r[1]}.')

    ## Levene's Test
    print(f"Homogeneity (Levene): {set1}-{set2} {var}")
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


print('============================================')
print('============================================')
print(describe(data['DIRECT']['correctness']))
print(describe(data['DECOMP_CONFIRM']['correctness']))
testHomogeneity('DIRECT', 'DECOMP_CONFIRM', 'correctness')
testNormality('DIRECT', 'correctness')
testNormality('DECOMP_CONFIRM', 'correctness')
print(ranksums(data['DIRECT']['correctness'], data['DECOMP_CONFIRM']['correctness']))

"""         success     failure
DECOMP      20          10
HUMAN       27          3
"""


table = np.array([[27, 3],[20, 10]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

print('============================================')
print('============================================')
print('TESTS')

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)


# count = [27, 20]
# nobs = [30, 30]
# print(proportions_ztest(count, nobs, alternative='larger'))


print('============================================')
print('============================================')


testNormality('DIRECT', 'correctness')
testNormality('VERIFIER', 'correctness')
testNormality('DECOMP', 'correctness')
testNormality('DECOMP_CONFIRM', 'correctness')


testHomogeneity('DIRECT', 'VERIFIER', 'correctness')
testHomogeneity('DIRECT', 'DECOMP', 'correctness')
testHomogeneity('DIRECT', 'DECOMP_CONFIRM', 'correctness')

testHomogeneity('VERIFIER', 'DECOMP', 'correctness')
testHomogeneity('VERIFIER', 'DECOMP_CONFIRM', 'correctness')

testHomogeneity('DECOMP', 'DECOMP_CONFIRM', 'correctness')

print('============================================')
print('============================================')

"""         success     failure
DECOMP      20          10
HUMAN       27          3
"""

print('============================================')
print('============================================')

ENCODING = 19
VERIFIER = 20
DECOMP = 20
HUMAN = 27

print('HUMAN-DECOMP')
X1 = HUMAN
X2 = DECOMP
table = np.array([[X1, 30-X1],[X2, 30-X2]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)

print('============================================')
print('============================================')

print('HUMAN-VERIFIER')
X1 = HUMAN
X2 = VERIFIER
table = np.array([[X1, 30-X1],[X2, 30-X2]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)

print('============================================')
print('============================================')

print('HUMAN-ENCODING')
X1 = HUMAN
X2 = ENCODING
table = np.array([[X1, 30-X1],[X2, 30-X2]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)

print('============================================')
print('============================================')

print('DECOMP-ENCODING')
X1 = DECOMP
X2 = ENCODING
table = np.array([[X1, 30-X1],[X2, 30-X2]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)

print('============================================')
print('============================================')

print('DECOMP-VERIFIER')
X1 = DECOMP
X2 = VERIFIER
table = np.array([[X1, 30-X1],[X2, 30-X2]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)

print('============================================')
print('============================================')

print('VERIFIER-ENCODING')
X1 = VERIFIER
X2 = ENCODING
table = np.array([[X1, 30-X1],[X2, 30-X2]])
M = table.sum()
n = table[0].sum()
N = table[:, 0].sum()
start, end = hypergeom.support(M, n, N)
hypergeom.pmf(np.arange(start, end+1), M, n, N)

res = fisher_exact(table, alternative='two-sided')
print('two-sided')
print(res)
res = fisher_exact(table, alternative='less')
print('less')
print(res)
res = fisher_exact(table, alternative='greater')
print('greater')
print(res)