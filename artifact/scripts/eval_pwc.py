import glob, sys, os, csv
import numpy as np
assert len(sys.argv) == 2

def perc_gain(new, old):
    gain = round((1 - (new / old)) * 100, 1)
    if gain == 0:
        return 0.0
    return gain

def get_scores(path):
    ret = {}
    with open(path) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            ret[row['solver']] = float(row['score'])
    return ret

scores = []
for file in glob.glob(f"{sys.argv[1]}/**/scores.csv", recursive=True):
    scores.append(
        get_scores(file)
    )
    
greedy, pw, pwl = [], [], []
for score in scores:
    assert 'SolverLogic' in score
    assert 'Greedy' in score
    assert 'PairWise' in score
    assert 'PairWiseLogic' in score
    greedy.append(
        perc_gain(new=score['SolverLogic'],old=score['Greedy'])
    )
    pw.append(
        perc_gain(new=score['SolverLogic'],old=score['PairWise'])
    )
    pwl.append(
        perc_gain(new=score['SolverLogic'],old=score['PairWiseLogic'])
    )
breakpoint()
print(np.median(greedy))
print(np.median(pw))
print(np.median(pwl))