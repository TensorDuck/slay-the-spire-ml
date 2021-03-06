"""train a model for all four characters and save it"""
import json
import os

import numpy as np

from slayer.features import Converter
from slayer.globals import RESOURCE_LOCATION
from slayer.model import SimpleFactorizer, CosineDistance

CHARACTERS = ["DEFECT", "IRONCLAD", "THE_SILENT", "WATCHER"]

if __name__ == "__main__":
    with open(os.path.join(RESOURCE_LOCATION, "victory.json"), "r") as f:
        data = json.load(f)

    for character in CHARACTERS:
        for model_type in ["factorizer", "cosine"]:
            converter = Converter(character)
            if model_type == "factorizer":
                model = SimpleFactorizer(character)
            elif model_type == "cosine":
                model = CosineDistance(character)
            else:
                raise ValueError("invalid model_type")

            # get matrix for specific character
            character_decks = []
            for row in data:
                if row["character"] == character:
                    character_decks.append(np.array(row["deck_final"]))
            mat = converter.get_matrix(character_decks)

            # train a model
            model.fit(mat)

            # save the model
            model.save()

