import streamlit as st
import numpy as np

from slayer.features import Converter
from slayer.model import SimpleFactorizer, CosineDistance

MODEL_TYPES = {"factorizer": SimpleFactorizer, "cosine": CosineDistance}


def get_models(character: str, model_type: str):
    if model_type in MODEL_TYPES.keys():
        return Converter(character), MODEL_TYPES[model_type](character).load()
    else:
        raise ValueError("invalid model_type")


if __name__ == "__main__":
    st.title("Slay the Spire Card Suggestions")
    character = st.selectbox(
        "Character", options=["IRONCLAD", "THE_SILENT", "DEFECT", "WATCHER"]
    )
    model_type = st.sidebar.radio("model", options=list(MODEL_TYPES.keys()))

    converter, factorizer = get_models(character, model_type)

    card_mapping = {name: idx for idx, name in enumerate(converter.all_cards)}
    cards = st.multiselect("Cars in your Deck:", options=converter.all_cards)

    # create a deck
    deck_cards = []
    for card in cards:
        n = st.number_input(
            f"{card} number:",
            key=card_mapping[card],
            value=1,
            min_value=0,
            max_value=100,
        )
        for i in range(n):
            deck_cards.append(card)

    # now run ML if there are actually cards
    if deck_cards:
        # predict what changse are needed
        predictions = factorizer.predict(converter.create_deck(np.array(deck_cards)))
        ideal_deck_changes = converter.inverse_create_deck(predictions)

        best = sorted(
            list(ideal_deck_changes.keys()), key=ideal_deck_changes.__getitem__
        )[::-1]

        st.header("Pick Ups")
        for card in best[:10]:
            count = ideal_deck_changes[card]
            st.write(f"{card}: {count}")

        st.header("Current Deck Scores")
        for card in best:
            count = ideal_deck_changes[card]
            if card in deck_cards:
                st.write(f"{card}: {count}")

        st.header("Tier List")
        for card in best:
            count = ideal_deck_changes[card]
            st.write(f"{card}: {count}")
