import os,glob,pdb,pickle,sys
import machsmt.settings as settings
from machsmt.smtlib import logic_list

def die(msg):
    print("[machsmt_build] Error: {}".format(msg))
    sys.exit(1)

def get_inst_path_core(logic,instance,path, instance_name):
    if os.path.exists(path + '/' + instance_name): return path + instance_name
    directories = [v.split('/')[-2] for v in glob.glob(path+'*/')]
    canidates = [dir for dir in directories if instance_name.startswith(dir)]
    canidates.sort(key=lambda x: len(x),reverse=True)
    for dir in canidates:
        ret = get_inst_path_core(logic,instance,path = path + dir + '/', instance_name = instance_name[len(dir):])
        if ret == None:
            continue
        else:
            return ret

def get_smtlib_file(path):
    split = path.split('/')
    for i in range(len(split)):
        if split[i] in logic_list:
            logic, inst = split[i], "".join([v for v in split[i+1:]])
            ret = get_inst_path_core(logic,inst,path=settings.SMTLIB_BENCHMARKS_DB + '/' +  logic + '/', instance_name=inst)
            if ret == None: raise FileNotFoundError
            else: return ret