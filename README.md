# fugue_ai
Generating music compositions in the style of the Baroque period. Term project for Stanford University's CS 221 (Artificial Intelligence) class in Fall 2015.

## Main files:
1. BachFugue.py
reads bach fugues from directory ./data
2. NoteData.py
parses Bach fugue data into features
3. Compose.py
makes the final composition based on the transition tables provided by NoteData

## Auxiliary files:
1. script.py: catches occasional errrors in Compose
1. Eval.py: evaluates how close two voice-leading features are with another
1. Query.py: contains important constants and helper functions to evaluate note transitions
1. Sample.py: prints out transitions tables
1. UnitTesting.py: confirms the time epochs are correct
1. FeatureExtractor.py: extract voice-leading, interval, and pitch features

## Getting started
This codebase runs on python 2.7.

The only nonstandard library is music21. `pip install music21` to install.
The output is streamed to MuseScore application. You would need to download the MuseScore app to output and view the resulting composistions at https://musescore.org
To make 1 compositions using Fugue 1 to 10:
- python BachFugue.py 1 1 10 
- python NoteData.py
- python script.py 1
