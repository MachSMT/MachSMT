from cgi import test
from torch import device, dtype
import torch.nn as nn
import torch.nn.functional as F
import torch
import torch.optim as optim

import copy
import tempfile
import pdb
import time
import os
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import Dataset, DataLoader
import numpy as np
from torch.utils.data import random_split
from sklearn.preprocessing import OneHotEncoder

torch.set_default_tensor_type('torch.FloatTensor')

# class OneHot:
#     def __init__(self, unknown_class=False, sparse=False) -> None:
#         self.mapping = {}
#         self.in_type = None
#         self.sparse = False
        
#     def fit(self, X):
#         vals = set(x for x in X)
#         self.mapping = {key:it for key,it in zip(sorted(vals),range(len(vals)))}
#         self.inverse_mapping = {v:k for k,v in self.mapping.items()}
        
#     def transform(self, X):
#         ret = []
#         for x in X:
#             y = [0] * len(self.mapping)
#             if x in self.mapping:
#                 y[self.mapping[x]] = 1
#             ret.append(y)
#         return np.array(ret)
        
#     def fit_transform(self, X):
#         self.fit(X) 
#         return self.transform(X)

#     def inverse_transform(self, X):
#         ret = []
#         breakpoint()
#         for x in X:
#             ret.append(self.inverse_mapping[np.argmax(x)])
#         return ret

class MLP_DataSet(Dataset):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        assert not self.X.isnan().any()
        assert not self.Y.isnan().any()

    def __getitem__(self, index):
        return self.X[index].float(), self.Y[index].float()

    def __len__(self):
        return len(self.X)


def perc_diff_loss(output, target):
    return torch.mean(torch.abs(output - target) / ((output + target) / 2.0))


class TabularMLP(nn.Module):
    def __init__(self,
                 layer_sizes=(100, 100),
                 batch_size=128,
                 optimizer='adam',
                 learning_rate=4 * 10 ** -4,
                 weight_decay=10 ** -4,
                 loss_func=torch.nn.MSELoss(),
                 layer_type=nn.Linear,
                 activation=F.relu,
                 train_device='cuda',
                 eval_device='cpu',
                 gamma=0.01,
                 dropout_proba=0.25,
                 gradiant_clip=.25,  # maybe do a gradient norm here?? #vineel
                 ):
        super(TabularMLP, self).__init__()
        assert optimizer in ['adam']
        self.layer_sizes = layer_sizes
        self.optimizer = optimizer
        self.built = False
        self.it=None
        self.batch_size = batch_size
        self.weight_decay = weight_decay
        self.learning_rate = learning_rate
        self.loss_func = loss_func
        self.loss_history = []
        self.err_history = []
        self.built = False
        self.layer_type = layer_type
        self.activation = activation
        self.train_device = train_device
        self.eval_device = eval_device
        self.gamma = gamma
        self.dropout = nn.Dropout(dropout_proba)
        self.eval()
        self.to(device=self.eval_device)
        self.gradiant_clip = gradiant_clip

    def forward(self, X):
        for it, _ in enumerate(self.layer_sizes):
            layer = self.__getattr__(f'layer_{it}')
            X = layer(X)
            bn = self.__getattr__(f"norm_{it}")
            X = bn(X)
            X = self.activation(X)
            X = self.dropout(X)  # might be faster to do dropout after
        return self.out(X)

    def build(self, in_shape, out_shape):
        self.in_shape = in_shape
        self.out_shape = out_shape
        _in, _out = self.in_shape, None

        for it_layer, layer_size in enumerate(self.layer_sizes):
            name = 'Deep Layer' if it_layer else 'Input Layer'
            print(f"{name} #{it_layer} shape={(_in, _out)}")
            _out = layer_size
            self.__setattr__(
                f'layer_{it_layer}',
                self.layer_type(_in, _out, bias=True)
            )
            self.__setattr__(f'norm_{it_layer}', nn.LayerNorm(_out))
            _in = _out
        print(f"Out Layer #{it_layer+1} shape={(_in, self.out_shape)}")
        self.__setattr__('out', self.layer_type(_in, self.out_shape, bias=True))

        if self.optimizer == 'adam':
            self.opt = torch.optim.Adam(
                self.parameters(),
                lr=self.learning_rate,
                weight_decay=self.weight_decay)
        else:
            raise NotImplementedError

        self.tot_params = sum(p.numel() for p in self.parameters())
        print(f"Built Novel DNN with {self.tot_params=}")
        self.built = True

    def fit(
            self,
            X,
            Y,
            max_epochs=10,
            max_time=1 * 60,
            batch_size=None,
            learning_rate=None,
            split_ratio=.15):
        self.to(device=self.train_device)
        torch.set_num_threads(os.cpu_count())
        Y = self.prepare_output(Y)
        dataset = MLP_DataSet(torch.Tensor(X), torch.Tensor(Y))
        n_test = round(len(X) * split_ratio)
        train_dataset, test_dataset = random_split(dataset, [len(X) - n_test, n_test])
        if not self.built:
            self.build(train_dataset.dataset.X.shape[1], len(train_dataset.dataset.Y[0]))

        if batch_size is not None:
            self.batch_size = batch_size
        if learning_rate is not None:
            self.set_learning_rate(learning_rate)

        start = time.time()
        if self.it is None: self.it = 0
        run_it = 0
        train_data_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        test_data_loader  = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=True)
        while time.time() - start < max_time and run_it < max_epochs:
            epoch_train_loss = self._train_epoch(train_data_loader)
            epoch_test_loss = self._test_epoch(test_data_loader)
            print(f"Epoch #{len(self.loss_history):6}, Loss={epoch_train_loss:.5E}, Err={epoch_test_loss:.5E}, lr={self.get_learning_rate():.2E}, bs={self.get_batch_size()} ds={len(X)}")
            self.it += 1; run_it += 1
        self.eval()
        self.to(device=self.eval_device)
        self.loss_hist, self.test_hist = [], []

    def _train_epoch(self, data_loader):
        self.train()
        self.to(device=self.train_device)
        running_loss = 0.
        for step, (x, y) in enumerate(data_loader):
            b_x, b_y = x.to(device=self.train_device), y.to(device=self.train_device)
            out = self(b_x)
            torch.no_grad()
            loss = self.loss_func(out, b_y)
            self.opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.parameters(), self.gradiant_clip)
            self.opt.step()
            running_loss += loss.item()
        return running_loss / len(data_loader)
                
    def _test_epoch(self, data_loader):
        self.eval()
        with torch.no_grad():
            running_loss = 0.
            for step, (x, y) in enumerate(data_loader):
                b_x, b_y = x.to(device=self.train_device), y.to(device=self.train_device)
                out = self(b_x)
                loss = self.loss_func(out, b_y)
                running_loss += loss.item()
        return running_loss / len(data_loader)

    def score(self, dataset):
        predictions = self.predict(torch.tensor(X, requires_grad=False))
        if self.gpu:
            predictions.cpu()
            predictions.detach().numpy()
        ret = 0.0
        for pred, gt in zip(predictions, Y):
            pred = float(pred)
            gt = float(gt)
            ret += np.abs(pred - gt) ** 2
        return (ret / len(predictions)) ** .5

    def get_learning_rate(self): return self.learning_rate

    def get_batch_size(self): return self.batch_size

    def set_batch_size(self, bs): self.batch_size = bs

    def set_learning_rate(self, lr):
        self.learning_rate = lr
        for param_group in self.opt.param_groups:
            param_group['lr'] = lr

    def loss(self): return self.loss_history[-1]

    def predict(self, X, with_probabilies=False):
        self.eval()
        ret = self(torch.Tensor(X)).detach().numpy()
        return self.postprocess_output(ret, with_probabilies)

    def logger(self, kwargs):
        breakpoint()
        

class TabularMLPRegressor(TabularMLP):
    def __init__(self, layer_sizes=(100, 100), batch_size=128, optimizer='adam', learning_rate=4 * 10 ** -4, weight_decay=10 ** -4, loss_func=torch.nn.MSELoss(), layer_type=nn.Linear, activation=F.relu, train_device='cuda', eval_device='cpu', gamma=0.01, dropout_proba=0.25, gradiant_clip=0.25):
        super().__init__(layer_sizes, batch_size, optimizer, learning_rate, weight_decay, loss_func, layer_type, activation, train_device, eval_device, gamma, dropout_proba, gradiant_clip)
    def prepare_output(self, Y):
        return Y
    
    def postprocess_output(self, Y, with_probabilies):
        if with_probabilies: raise NotImplementedError
        return Y
        
class TabularMLPClassifier(TabularMLP):
    def __init__(self, layer_sizes=(100, 100), batch_size=128, optimizer='adam', learning_rate=4 * 10 ** -4, weight_decay=10 ** -4, loss_func=torch.nn.CrossEntropyLoss(), layer_type=nn.Linear, activation=F.relu, train_device='cuda', eval_device='cpu', gamma=0.01, dropout_proba=0.25, gradiant_clip=0.25):
        super().__init__(layer_sizes, batch_size, optimizer, learning_rate, weight_decay, loss_func, layer_type, activation, train_device, eval_device, gamma, dropout_proba, gradiant_clip)
        self.output_one_hot = None
    
    def prepare_output(self, Y):
        assert len(Y.shape) == 1, "1 diminsional vector only"
        if self.output_one_hot is None:
            self.output_one_hot = OneHotEncoder(sparse=False)
            return self.output_one_hot.fit_transform(Y.reshape(-1, 1))
        else:
            return self.output_one_hot.transform(Y)
        
    def postprocess_output(self, Y, with_probabilies=False):
        from scipy.special import softmax
        probas = softmax(Y,axis=1)
        ret = self.output_one_hot.inverse_transform(probas).flatten()
        if with_probabilies: return ret,probas
        else: return ret


if __name__ == '__main__':
    from sklearn import datasets
    X, Y = datasets.load_boston(return_X_y=True)

    dnn = TabularMLPRegressor(layer_sizes=(1000,) * 6)
    dnn.fit(X, Y.reshape(-1, 1))

## are you working now?

