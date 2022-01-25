"""For preprocessing input data

The expected format of a record is:

record = {
    "event": {
        ...
    }
}

"""
import os

import numpy as np

from slayer.globals import RESOURCE_LOCATION


def process_card_name(name: str) -> str:
    """convert card_name to a uniform format"""
    # remove any upgrades. Typically this is a +1 at the end
    # edge-case is seering blow which allows for +1->infinity
    name = name.split("+")[0]
    # remove color name for different strikes, i.e. strike_g
    # these cards are functionally all the same, but have different artwork in game
    name = name.split("_")[0]
    # remove all whitespace and standardize case
    return name.strip().lower().replace(" ", "_")


def get_character(record: dict) -> list:
    return record.get("event").get("character_chosen")  # there are null record


def get_cards(record: dict) -> list:
    """read a record and uniform card names"""
    all_cards = []
    for card in record["event"]["master_deck"]:
        all_cards.append(process_card_name(card))
    return all_cards


def filter_records_by_character(records: list, character: str) -> list:
    """Filter out records for a specific character"""
    specific_records = []
    for record in records:
        if get_character(record) == character:
            specific_records.append(record)

    return specific_records

def record_is_normal_game(record: dict) -> bool:
    """Return True if the record is a normal game, otherwise False"""
    return not (record["event"]["is_prod"] or record["event"]["is_daily"] or record["event"]["is_endless"])

def record_is_victory(record: dict) -> bool:
    """Return True if the record shows a victory"""
    return record["event"]["victory"]

def record_is_high_ascension(record: dict, min_ascension=15):
    """Return True if the record is for a player of a certain ascension level

    High Ascension level indicates high skill for a number of reasons:
    * Player has played numerous games
    * Player has a more difficult game each time
    * Player is forced to make tighter choices with card picks

    While not perfect, this is a good proxy absent any official leaderboard.
    """
    return record["event"]["ascension_level"] >= min_ascension

def filter_records(records: list, condition_func_list: list) -> list:
    """Filter out records based on a list of conditions"""
    specific_records = []
    for record in records:
        if all([func(record) for func in condition_func_list]):
            specific_records.append(record)

    return specific_records


def get_all_unique_cards_and_relics(records: list) -> set:
    """Process multiple records and return a matrix of card counts"""
    all_cards = {}
    all_relics = {}
    for dat in records:
        character = get_character(dat)
        if character is None:
            print(dat)
        else:
            if character not in all_cards:
                all_cards[character] = set()
            if character not in all_relics:
                all_relics[character] = set()
            all_cards[character] = all_cards[character].union(get_cards(dat))
            all_relics[character] = all_relics[character].union(dat["event"]["relics"])

    return all_cards, all_relics

def make_resources(records: list):
    """Process multiple records and produce resource files"""
    all_cards, all_relics = get_all_unique_cards_and_relics(records)
    for character in all_cards:
        np.save(
            os.path.join(RESOURCE_LOCATION, f"{character}_cards.npy"),
            sorted(list(all_cards[character])),
        )
        np.save(
            os.path.join(RESOURCE_LOCATION, f"{character}_relics.npy"),
            sorted(list(all_relics[character])),
        )

def make_abridged_record(record: dict):
    """Make an abridged record to reduce saved output size"""
    return {
        "character": get_character(record),
        "deck_final": get_cards(record),
        "relics": record["event"]["relics"],
        "victory": record["event"]["victory"],
        "ascension_level": record["event"]["ascension_level"]
    }