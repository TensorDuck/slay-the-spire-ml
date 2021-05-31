# Slay the Spire ML

This is just a fun mini-project to create a card recommendation system for the game Slay the Spire.
It took data (supplied by the game creators) from this mirror:
https://archive.org/details/slay-the-data.-7z

## Goal

The goal is to take a player's current deck and recommend cards that would help round out the deck and fix gaps.

To accomplish that, I want to experiment with different collaborative filtering methods to mine data form successful runs. For a brief introduction to collaborative filtering, take a look at this:
https://developers.google.com/machine-learning/recommendation/collaborative/basics

## Quickstart

The intention is to access the dashboard from the streamlit app. This can be done with the commands:

```
streamlit run app.py
```

## Dev TODO
* Add streamlit docker container for easier deployment