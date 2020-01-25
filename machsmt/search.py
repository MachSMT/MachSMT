import os,glob,pdb,pickle,sys

use_cache = True
cache = {}
n=0

def get_inst_path(theory,instance):
    global n,cache
    if theory in cache and instance in cache[theory]:
        return cache[theory][instance]
    if n == 0 and use_cache:
        if os.path.exists('lib/fs.p'):
            cache = pickle.load(open('lib/fs.p','rb'))

    ret = get_inst_path_core(theory,instance,path='benchmarks/' + theory + '/', instance_name=instance)
    if ret == None:
        print("Failed to find: " + theory + ',' + instance)
        raise RuntimeError
    n+=1
    if n%1000 == 0:
        pickle.dump(cache,open('lib/fs.p','wb'))
        n+=1
    return ret

def get_inst_path_core(theory,instance,path, instance_name):
    if os.path.exists(path + '/' + instance_name):
        return path + '/' + instance_name
    else:
        canidates = []
        directories = [v.split('/')[-2] for v in glob.glob(path+'*/')] 
        for dir in directories:
            if instance_name.startswith(dir):
                canidates.append(dir)
        canidates.sort(key=lambda x: len(x),reverse=True)
        for c in canidates:
            ret = get_inst_path_core(theory,instance,path = path + c + '/', instance_name = instance_name[len(c):])
            if ret == None:
                continue
            else:
                return ret
    return None