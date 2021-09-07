
class PortfolioRegressor:
    def __init__(self, regressors = None) -> None:
        self.regressors = {} if regressors is None else regressors
        self.best = None
        self.scores = {}

    def add_regressor(self, name, regressor): 
        self.regressors[name] = regressor

    def eval(self, X, Y):
        self.scores = {}
        Ys = {}
        for it, regressor in enumerate(self.regressors):
            Ys[regressor] = self.regressors[regressor].eval(X, Y)
            self.scores[regressor] = self.regressors[regressor].metrics(Y, Ys[regressor])['mean_squared_error']
        self.best = min(self.scores, key=self.scores.get)
        return Ys[self.best]

    def train(self, X, Y):
        self.eval(X, Y)
        return self.regressors[self.best].train(X, Y)

    def predict(self, X):
        return self.regressors[self.best].predict(X)

    def __str__(self):
        return f'PortfolioRegressor({self.best=})'
    __repr__ = __str__