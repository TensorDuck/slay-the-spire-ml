"""For preprocessing input data"""
import os

import numpy as np

from slayer.globals import RESOURCE_LOCATION


def process_card_name(name: str) -> str:
    """convert card_name to a uniform format"""
    return name.strip().lower().replace(" ", "_").rstrip("+1")


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


def filter_records_by_victory(records: list) -> list:
    """Filter out records for a specific character"""
    specific_records = []
    for record in records:
        if record["event"]["victory"]:
            specific_records.append(record)

    return specific_records


def get_all_unique_cards(records: list) -> set:
    """Process multiple records and return a matrix of card counts"""
    all_cards = {}
    for dat in records:
        character = get_character(dat)
        if character is None:
            print(dat)
        else:
            if character not in all_cards:
                all_cards[character] = set()
            all_cards[character] = all_cards[character].union(get_cards(dat))

    return all_cards


def make_resources(records: list):
    """Process multiple records and produce resource files"""
    all_cards = get_all_unique_cards(records)
    for character in all_cards:
        np.save(
            os.path.join(RESOURCE_LOCATION, f"{character}_cards.npy"),
            sorted(list(all_cards[character])),
        )
