"""For producing recommendation matrices for training new models"""
import os

import numpy as np
from sklearn.decomposition import NMF
from sklearn.preprocessing import OneHotEncoder

from slayer.globals import RESOURCE_LOCATION


class Converter:
    def __init__(self, character_name: str):
        """A converter for converting JSON records into reaction matrix"""
        self.character_name = character_name
        self.all_cards = np.load(
            os.path.join(RESOURCE_LOCATION, f"{self.character_name}_cards.npy")
        )
        self.n_cards = len(self.all_cards) + 1

        # make an encoder that maps unknown cards to the last column
        self.encoder = OneHotEncoder(
            categories=[self.all_cards], handle_unknown="ignore", sparse=False
        )
        self.encoder.fit([["test"], ["new_test"]])  # initialize the encoder

    def create_deck(self, cards: np.ndarray) -> np.ndarray:
        """Take a given list of card names and convert it to an array deck"""
        result = self.encoder.transform(cards.reshape(-1, 1)).sum(axis=0)
        return result

    def inverse_create_deck(self, deck: np.ndarray):
        """Convert a deck array into a dictionary of card-names and counts"""
        return {self.all_cards[idx]: count for idx, count in enumerate(deck)}

    def get_matrix(self, deck_list: list):
        """Get a reaction matrix for all cards in a list of decks"""
        all_rows = []
        for deck in deck_list:
            row = self.create_deck(deck)
            all_rows.append(row)

        return np.stack(all_rows)

    def get_embeddings(self, records: list):
        """For making embeddings on the players and records"""
        mat = self.get_matrix(records)
        self.matrix_factorizer = NMF(n_components=5)
        return (
            self.matrix_factorizer.fit_transform(mat),
            self.matrix_factorizer.components_,
        )
