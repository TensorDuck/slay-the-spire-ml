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

### Running Go Scripts

I used Go1.16.5 for running the scripts.
Later versions of Go should also work, but it is not tested.

## Dev TODO
* Improve model (currently has very poor recommendations)
* Clean up data
  * exclude daily challenge games
  * include relics
  * include close wins (i.e. getting to act 3)
* Add picks depending on which act the player is in
* Also include aggregate pathing information - i.e. target paths
*