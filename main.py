import glob , pdb, pickle
from db import DB
from selector import LearnedModel
from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from operator import itemgetter

def model_maker(pca=True):
    # pca = False
    if pca:
        return make_pipeline(
            StandardScaler(),
            PCA(n_components=10),
            AdaBoostRegressor()
            #MLPRegressor(hidden_layer_sizes=(100,100,50,50,10,10,10,5,5,5), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, power_t=0.5, max_iter=20000000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=100)
        )
    else:
        return make_pipeline(
            StandardScaler(),
            AdaBoostRegressor()
            #MLPRegressor(hidden_layer_sizes=(100,100,50,50,10,10,10,5,5,5), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, power_t=0.5, max_iter=20000000, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=100)
        )

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