"""For modelling a record"""
import os
import pickle

import numpy as np
from sklearn.decomposition import NMF

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
