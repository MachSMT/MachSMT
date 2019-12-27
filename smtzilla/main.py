import glob , pdb, pickle
from db import DB
from selector import LearnedModel
from operator import itemgetter

build_db = True
db = None
if build_db:
    db = DB()
    db.build()
    db.tidy()
    pickle.dump(db, open( "bin/db.lib", "wb" ))
else:
    db = pickle.load(open( "bin/db.lib", "rb" ))
print("DB Created.")



theory_track_N_pairs = []
for theory in db.db:
    for track in db.db[theory]:
        inputs = set()
        for solver in db.db[theory][track]:
            for inp in db.db[theory][track][solver]:
                inputs.add(inp)
        theory_track_N_pairs.append((theory,track,len(inputs)))
theory_track_N_pairs.sort(key=itemgetter(2),reverse=False)
print(theory_track_N_pairs)


# import time
# tic = time.time()
# lm = LearnedModel(
#     theory='UFIDL',
#     track='smt-comp/2019/results/Single_Query_Track',
#     db=db.db['UFIDL']['smt-comp/2019/results/Single_Query_Track'],
#     model_maker=model_maker
# )
# lm.calc_features()
# lm.eval_and_build()
# lm.plot()
# print("TIME: " + str(time.time() - tic))

for theory,track,n in theory_track_N_pairs:
    print(theory,track,n)
    if theory == 'QF_UFIDL' or theory == 'UFLIA' or n < 75:
        print("Skipping")
        continue
    lm = LearnedModel(
        theory=theory,
        track=track,
        db=db.db[theory][track],
        model_maker=model_maker
    )      
    lm.calc_features()
    lm.eval_and_build()
    lm.plot()