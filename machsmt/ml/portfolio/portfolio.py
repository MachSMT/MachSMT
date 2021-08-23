
class PortfolioRegressor:
    def __init__(self, regressors={}) -> None:
        self.regressors = regressors
        self.best = None

    def add_regressor(self, name, regressor): 
        self.regressors[name] = regressor

    def eval(self, X, Y):
        best = float('inf')
        ret = None
        for it, regressor in enumerate(self.regressors):
            Y_ = self.regressors[regressor].eval(X, Y)
            score = self.regressors[regressor].metrics(Y, Y_)['mean_squared_error']
            if score < best:
                best = score
                self.best = regressor
                ret = Y_
        return ret

    def train(self, X, Y):
        if not self.best:
            self.eval(X, Y)
        return self.regressors[self.best].train(X, Y)

    def predict(self, X):
        if not self.best:
            raise ValueError
        return self.regressors[self.best].predict(X)
