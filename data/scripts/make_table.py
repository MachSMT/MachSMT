import argparse
import math
import os
import sys
import csv

def perc_diff(v1, v2):
    return round((v1 - v2) / ((v1 + v2) / 2) * 100, 1)

def perc_improvement(ehm, baseline):
    return round((1 - ehm / baseline) * 100, 1)

def perc_gain(new, old):
    gain = round((1 - (new / old)) * 100, 1)
    if gain == 0:
        return 0.0
    return gain

def mark_best(ehm, impr):
    if impr > 0:
        return f'\\textbf{{{ehm}}}'
    return str(ehm)

def get_logic_info(csvfile):

    benchmarks = set()
    solvers = set()
    scores = dict()
    with open(csvfile, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            benchmarks.add(row['benchmark'])
            solvers.add(row['solver'])

            if row['solver'] not in scores:
                scores[row['solver']] = 0
            scores[row['solver']] += float(row['score'])

    return len(benchmarks), len(solvers), scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('results_dir')
    args = ap.parse_args()

    if not os.path.exists(args.results_dir):
        sys.exit("Results directory does not exist")

    machsmt_configs = ('Random', 'Greedy', 'SolverLogic', 'PairWiseLogic')
    vbs_config = 'Oracle'

    track_csv_dir = {'INC': 'incremental', 'SQ': 'single-query'}

    for year in (2019, 2020):
        dir_year = os.path.join(args.results_dir, str(year))
        if not os.path.exists(dir_year):
            print(f"No results for {year} found")
            continue

        nskipped = 0
        for track in ('INC', 'SQ'):
            table_rows = []
            dir_track = os.path.join(dir_year, track)
            if not os.path.exists(os.path.join(dir_track)):
                print(f"No results for {year}/{track} found")
                continue

            for logic in os.listdir(dir_track):
                scores = os.path.join(dir_track, logic, 'scores.csv')
                if not os.path.exists(scores):
                    sys.exit(f"No scores.csv file found for {dir_track}")

                logic_csv = os.path.join('csv', str(year), track_csv_dir[track], f'{logic}.csv')
                nbenchmarks, nsolvers, par2_scores = get_logic_info(logic_csv)

                # Skip logics with less than 25 benchmarks
                if nbenchmarks < 25:
                    nskipped += 1
                    continue

                results = []
                with open(scores, 'r') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        results.append((float(row['score']), row['solver']))
                        if row['solver'] in par2_scores:
                            machsmt_score = round(float(row['score']), 1)
                            csv_score = round(par2_scores[row['solver']], 1)
                            if machsmt_score != csv_score:
                                print(f"warning: incorrect PAR2 score for {row['solver']} detected in {year}/{track}/{logic}: {machsmt_score} vs. {csv_score}")

                smt_comp_solvers = [x for x in results if x[1] not in machsmt_configs and x[1] != vbs_config and not x[1].endswith(")")]
                if not smt_comp_solvers:
                    continue

                winner = smt_comp_solvers[0]
                vbs_solver = None
                random_solver = None
                ehm_solver = None
                for res in results:
                    if res[1] == vbs_config:
                        vbs_solver = res
                    elif res[1] == 'Random':
                        random_solver = res
                    elif res[1] == 'SolverLogic':
                        ehm_solver = res
                assert vbs_solver
                assert random_solver
                assert ehm_solver

                table_rows.append((
                    f"{logic} ({nbenchmarks})".replace('_', '\\_'),
                    winner[1],
                    round(random_solver[0], 1),#perc_diff(random_solver[0], ehm_solver[0]),
                    round(winner[0], 1),#perc_diff(winner[0], ehm_solver[0]),
                    round(vbs_solver[0], 1),#perc_diff(ehm_solver[0], vbs_solver[0])
                    round(ehm_solver[0], 1),
                    perc_gain(ehm_solver[0], winner[0])
                    )
                )

            table_rows = sorted(table_rows, key=lambda x: x[6], reverse=True)

            table = ""
            table += """\\begin{tabular}{l@{\\hspace{1em}}lrrrrr}
\\toprule
\\multirow{2}{*}{\\textbf{Logic in """
            table += f"{track}'{year-2000}"
            table += """}} &
\\multirow{2}{*}{\\textbf{Best}} &
\\multicolumn{4}{c}{\\textbf{PAR-2}} \\\\
&
&
\\textbf{Random} &
\\textbf{Best} &
\\textbf{VBS} &
\\textbf{\\machsmtlehm} &
\\textbf{Impr. [\\%]}
\\\\
\\midrule
"""
            for row in table_rows:
                row = (row[0], row[1], str(row[2]), str(row[3]), str(row[4]), mark_best(row[5], row[6]), mark_best(row[6], row[6]))
                table += '{0:20s} & {1:12s} & {2:11s} & {3:11s} & {4:11s} & {5:11s} & {6:4s}\\\\\n'.format(*row)

            table += "\\bottomrule\n\\end{tabular}"

            with open(f'table_{track.lower()}_{year}.tex', 'w') as outfile:
                outfile.write(table)

            print(f"skipped {nskipped} logics in {year}/{track}")



if __name__ == '__main__':
    main()
