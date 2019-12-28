import os,glob
def get_inst_path(theory,instance):
    path = 'benchmarks/' + theory + '/'
    instance_name = instance
    if os.path.exists(path + '/' + instance):
        return path + '/' + instance
    else:
        canidates = [None]
        while len(canidates) > 0:
            canidates = []
            directories = [v.split('/')[-2] for v in glob.glob(path+'*/')] 
            for dir in directories:
                if instance_name.startswith(dir):
                    canidates.append(dir)
            best , longest = None,0
            for c in canidates:
                if len(c) > longest:
                    best = c
                    longest = len(c)
            if best != None:         
                path = path + best + '/'
                instance_name = instance_name[len(best):]
    if os.path.exists(path + '/' + instance_name):
        return path + '/' + instance_name
    else:
        print("Failed to find: " + theory + ',' + instance)
        return None
