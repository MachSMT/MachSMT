

'''
To add an extra feature, define a function anywhere in this module/file.

All functions that appear in this model will be automatically included in the ML model.

INPUT
The function siguature should include the following:

    file_path - absolute path to smt2 input as string
    logic - string of the logic of the smt2 input in { 'ALIA', 'AUFDTLIA', 'AUFLIA', 'AUFLIRA', 'AUFNIRA', 'BV', 'BVFP', 'FP', 'LIA', 'LRA', 'NRA', 'QF_ABV', 'QF_ALIA', 'QF_AUFBV', 'QF_AUFLIA', 'QF_AX', 'QF_BV', 'QF_BVFP', 'QF_FP', 'QF_IDL', 'QF_LIA', 'QF_LRA', 'QF_NIA', 'QF_NRA', 'QF_RDL', 'QF_UF', 'QF_UFBV', 'QF_UFLIA', 'QF_UFLRA', 'QF_UFNIA', 'QF_UFNRA', 'UF', 'UFBV', 'UFDT', 'UFDTLIA', 'UFIDL', 'UFNIA'}
    track  - string of the track of the smt2 input in { 'Single_Query_Track', 'Incremental_Track', 'Unsat_Core_Track', 'Challenge_Track_non-incremental', 'Challenge_Track_incremental' }

OUTPUT
    
    A single floating point number denoting a feature to be considered for this logic/track

    OR

    None if the feature should not be considered for this logic/track

'''


# def example_feature(file_path,logic,track):
#     import random
#     if logic == 'FP' or logic == 'QF_FP':     #feature if FP specific
#         return random.random()                  #Calculate feature value. Will be automaticall scalled + ran through PCA later.
#     else:
#         return None                             #Do not consider this feature for this logic/track
