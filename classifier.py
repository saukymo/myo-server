from sklearn import neighbors
import numpy as np

SUBSAMPLE = 2
K = 20


class NNClassifier:
    """A wrapper for sklearn's nearest-neighbor classifier"""

    cluster = 3
    nn = None

    def __init__(self):
        self.read_data()

    def read_data(self):
        X = []
        Y = []
        for i in range(self.cluster):
            X.append(np.fromfile('data/vals%d.dat' % i, dtype=np.uint16).reshape((-1, 8)))
            Y.append(i + np.zeros(X[-1].shape[0]))

        self.train(np.vstack(X), np.hstack(Y))

    def train(self, X, Y):
        self.X = X
        self.Y = Y
        if self.X.shape[0] >= K * SUBSAMPLE:
            self.nn = neighbors.KNeighborsClassifier(n_neighbors=K, algorithm='kd_tree')
            self.nn.fit(self.X[::SUBSAMPLE], self.Y[::SUBSAMPLE])

    def classify(self, d):
        if self.X.shape[0] < K * SUBSAMPLE:
            return 0
        return int(self.nn.predict(np.array(d).reshape(1, -1))[0])
