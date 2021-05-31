import streamlit as st
import numpy as np

from slayer.features import Converter
from slayer.model import SimpleFactorizer


def get_models(character):
    return Converter(character), SimpleFactorizer(character).load()


if __name__ == "__main__":
    st.title("Slay the Spire Card Suggestions")
    character = st.selectbox("Character", options=["IRONCLAD", "THE_SILENT", "DEFECT"])

    converter, factorizer = get_models(character)

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

        st.header("Pick Ups")
        for card, count in ideal_deck_changes.items():
            if count >= 1:
                st.write(f"{card}: {count}")

        st.header("Removals")
        for card, count in ideal_deck_changes.items():
            if count <= -1:
                st.write(f"{card}: {count}")

        st.header("Indifferent")
        for card, count in ideal_deck_changes.items():
            if (count < 1) and (count > -1):
                st.write(f"{card}: {count}")
