


class DB:
    def __init__(self):
        self.db = {}
    def add(self,theory,solver,instance,data):
        if theory not in self.db:
            self.db[theory] = {}
        if solver not in self.db[theory]:
            self.db[theory][solver] = {}
        if instance not in self.db[theory][solver]:
            self.db[theory][solver][instance] = None
        self.db[theory][solver][instance] = data
    def summary(self):
        for theory in self.db:
            print(theory)
            for solver in self.db[theory]:
                print("\t" + solver + "\t" + str(len(self.db[theory][solver])))