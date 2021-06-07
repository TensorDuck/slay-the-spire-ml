"""For modelling a record"""
import os
import pickle

import numpy as np
from scipy import sparse
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_distances

from slayer.globals import RESOURCE_LOCATION


class SimpleFactorizer:
    def __init__(self, name: str):
        self.name = name
        self.fname = os.path.join(
            RESOURCE_LOCATION, f"{self.name}_SimpleFactorizer.pkl"
        )
        self.factorizer = NMF()

    def fit(self, reaction_matrix: np.ndarray):
        self.factorizer.fit(reaction_matrix)

    def predict(self, deck_contents: np.ndarray):

        # determine contents of final deck
        player_embedding = self.factorizer.transform([deck_contents])
        final_deck = self.factorizer.inverse_transform(player_embedding)

        diff = final_deck[0, :] - deck_contents
        return diff

    def save(self):
        pickle.dump(self.factorizer, open(self.fname, "wb"))

    def load(self):
        self.factorizer = pickle.load(open(self.fname, "rb"))
        return self


class CosineDistance:
    def __init__(self, name: str, n_best: int = 10):
        self.name = name
        self.n_best = n_best
        self.fname = os.path.join(RESOURCE_LOCATION, f"{self.name}_CosineDistance.npy")

    def fit(self, reaction_matrix: np.ndarray):
        self.internal_data = reaction_matrix

    def predict(self, deck_contents: np.ndarray):
        # calcualte cosine distance with all the known decks
        distances = cosine_distances(
            deck_contents.reshape((1, -1)), self.internal_data
        ).flatten()

        # find the n-th best decks and average their contents
        nth_best = np.sort(distances)[self.n_best - 1]
        average_deck = self.internal_data[distances < nth_best].mean(axis=0)

        # return the difference between the average deck and deck-contents
        diff = average_deck - deck_contents
        return diff

    def save(self):
        np.save(self.fname, self.internal_data)

    def load(self):
        self.internal_data = np.load(self.fname)
        return self
