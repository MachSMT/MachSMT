import sys, os, argparse
import csv

TIMEOUT_2019 = 2400
TIMEOUT_2020 = 1200

def compute_par2_incremental(correct, wrong, num_check_sat, time_required, time_limit):
    if wrong > 0:
        return 10 * wrong * time_limit
    return time_required + (2 * time_limit / num_check_sat) * (num_check_sat - correct)

def compute_par2(answer, expected, time_required, time_limit):
    # unkonwn answer or time limit reached
    if answer not in ('sat', 'unsat') or time_required >= time_limit:
        return 2 * time_limit

    assert time_required < time_limit

    # Wrong answer
    if expected in ('sat', 'unsat') and answer != expected:
        return 10 * time_limit

    return time_required

def split_csv_single_query(reader, time_limit, benchmark_dir):

    file_cache_mis = dict()
    data = dict()
    for row in reader:
        benchmark = row['benchmark']
        solver = row['solver']
        time = float(row['wallclock time'])
        answer = row['result']
        expected = row['expected']

        logic = benchmark.split('/')[0]

        if logic not in data:
            data[logic] = []

        benchmark = os.path.join(benchmark_dir, benchmark)
        if not os.path.exists(benchmark):
            sys.exit(f"Could not find '{benchmark}'")

        if is_misclassified(benchmark, logic, file_cache_mis):
            print(f"misclassified benchmark: {benchmark}")
            continue

        d = dict()
        d['benchmark'] = benchmark
        d['solver'] = solver
        d['score'] = compute_par2(answer, expected, time, time_limit)
        data[logic].append(d)

    return data

def is_misclassified(benchmark, logic, file_cache):
    if benchmark in file_cache:
        return file_cache[benchmark]

    set_logic = ""
    with open(benchmark, 'r') as infile:
        for line in infile:
            if line.strip().startswith('(set-logic'):
                set_logic = line.replace('(set-logic', '').replace(')', '').strip()
                break

    return logic != set_logic

def get_num_check_sat(benchmark, file_cache):
    if benchmark in file_cache:
        return file_cache[benchmark]

    nchecksat = 0
    with open(benchmark, 'r') as infile:
        for line in infile:
            if line.strip().startswith('(check-sat)'):
                nchecksat += 1
    if nchecksat == 0:
        sys.exit(f"Error: no check-sat calls in {benchmark}")
    file_cache[benchmark] = nchecksat
    return nchecksat

def split_csv_incremental(reader, time_limit, benchmark_dir):
    file_cache = dict()
    file_cache_mis = dict()
    data = dict()
    for row in reader:
        benchmark = row['benchmark']
        solver = row['solver']
        time = float(row['wallclock time'])
        correct = int(row['correct-answers'])
        wrong = int(row['wrong-answers'])

        logic = benchmark.split('/')[0]

        if logic not in data:
            data[logic] = []

        benchmark = os.path.join(benchmark_dir, benchmark)
        if not os.path.exists(benchmark):
            sys.exit(f"Could not find '{benchmark}'")

        if is_misclassified(benchmark, logic, file_cache_mis):
            print(f"misclassified benchmark: {benchmark}")
            continue

        nchecksat = get_num_check_sat(benchmark, file_cache)

        # Skip incremental benchmarks with only one check-sat call
        if nchecksat == 1:
            continue

        d = dict()
        d['benchmark'] = benchmark
        d['solver'] = solver
        d['score'] = compute_par2_incremental(correct, wrong, nchecksat, time, time_limit)
        data[logic].append(d)

    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv')
    ap.add_argument('year', type=int)
    ap.add_argument('benchmark_dir')
    ap.add_argument('outdir')
    ap.add_argument('--incremental', action='store_true', default=False)
    args = ap.parse_args()

    assert args.year in (2019, 2020)

    if args.year == 2019:
        time_limit = TIMEOUT_2019
    else:
        time_limit = TIMEOUT_2020

    if not os.path.exists(args.benchmark_dir):
        sys.exit(f"Benchmark directory '{args.benchmark_dir}' does not exist.")


    logics = dict()
    with open(args.csv) as csvfile:
        reader = csv.DictReader(csvfile)
        if args.incremental:
            logics = split_csv_incremental(reader, time_limit, args.benchmark_dir)
        else:
            logics = split_csv_single_query(reader, time_limit, args.benchmark_dir)

    remove_logics = []
    for logic, data in logics.items():
        benchmarks = set()
        for d in data:
            benchmarks.add(d['benchmark'])
        if len(benchmarks) < 25:
            print(f"{logic} only has {len(benchmarks)} benchmarks, remove...")
            remove_logics.append(logic)

    for logic in remove_logics:
        del logics[logic]

    # Remove duplicate entries with -fixed versions
    remove_duplicates = dict()
    for logic, data in logics.items():
        for row in data:
            if row['solver'].endswith('-fixed'):
                if row['benchmark'] not in remove_duplicates:
                    remove_duplicates[row['benchmark']] = []
                remove_duplicates[row['benchmark']].append(row['solver'].replace('-fixed', ''))

    num_results = dict()
    for logic, data in logics.items():
        num_results[logic] = dict()
        with open(os.path.join(args.outdir, f'{logic}.csv'), 'w') as outfile:
            keys = ['benchmark', 'solver', 'score']
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            for row in data:
                # Skip data from buggy solvers
                if row['benchmark'] in remove_duplicates and row['solver'] in remove_duplicates[row['benchmark']]:
                    #print(f"remove {row['benchmark']} for {row['solver']}")
                    continue

                row['solver'] = row['solver'].replace('-fixed', '')

                # Count number of data points for solver in a logic
                if row['solver'] not in num_results[logic]:
                    num_results[logic][row['solver']] = 0
                num_results[logic][row['solver']] += 1

                writer.writerow(row)

    # Sanity check: Check if we have the same number of data points for each
    # solver in a logic
    for logic, solvers in num_results.items():
        if len(set(solvers.values())) != 1:
            print(f"Logic {logic} does not have complete data:\n{solvers}")


if __name__ == '__main__':
    main()
