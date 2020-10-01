import glob,csv,pdb
from .util import logic_list,get_smtlib_file,get_checksats
from ..parser import args as settings
from ..util import die,warning

def get_contest_data(files):
    ## Build data structure of all data
    smtcomp = {}
    pdb.set_trace()
    loc = 'smt-comp/' + str(year) + '/csv/' if year != 2019 else 'smt-comp/' + str(year) + '/results/'
    for file in glob.glob(loc + '*.csv'):
        track = file.split('.')[0]
        smtcomp[track] = {}
        with open(file) as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                    logic = None
                    for v in row['benchmark'].split('/'):
                        if v in logic_list: 
                            logic = v
                            break
                    assert logic != None
                    if logic not in smtcomp[track]: smtcomp[track][logic] = {}
                    if row['solver'] not in smtcomp[track][logic]: smtcomp[track][logic][row['solver']] = {}
                    score = None
                    try:
                        path = get_smtlib_file(row['benchmark'])
                    except:
                        warning("Could not find: " + row['benchmark'] + ", skipping for now.")
                        continue
                    try:    ## compute score from SQ styled input file
                        if row['result'] != row['expected'] and row['expected'] != 'starexec-unknown' and row['result'] != 'starexec-unknown':
                            score = 10 * settings.timeout
                        elif float(row['wallclock time']) >= settings.timeout or row['result'] == 'starexec-unknown': score = 2 * settings.timeout
                        else: score = float(row['wallclock time'])
                    except KeyError: ## compute score from INC styled input file
                        try:
                            check_sats = get_checksats(path)
                        except IndexError:
                            warning(path + " is not in the working database. Skipping.")
                            continue
                        score = float(row['wallclock time']) + (2 * settings.timeout / check_sats) * (check_sats - int(row['correct-answers'])) + 10 * settings.timeout * int(row['wrong-answers'])
                    smtcomp[track][logic][row['solver']][path] = score
    return smtcomp