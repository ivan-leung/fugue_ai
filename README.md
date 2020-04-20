# fugue_ai
Generating music compositions in the style of the Baroque period. Term project for Stanford University's CS 221 (Artificial Intelligence) class in Fall 2015.

## Introduction
The ability for machines to create aesthetically pleasing works has been the subject of many debates. In the past few decades, many machines have been designed to produce original artworks in an attempt to demonstrate the potentials for machines to learn and to create. Notable AI machines include AARON, a 'Cybernetic Artist' developed by Harold Cohen that paints , and Emily 1 Howell2, a computer program written by David Cope to compose music. This project aims to add to the community of AI artists in the realm of music composition. In particular, this project will learn from the wealth of works in the Baroque period in to produce pleasing chorales and fugues.

## Task Definition
This project will focus on music compositions in the Baroque Period. In particular, this project will attempt to generate works in the forms of fugues. The Baroque Period is chosen because many composition rules are strictly observed; the consistency of compositional conventions will aid the learning process of the AI program. Further, the results of the AI compositions have more objective evaluation compared to romantic or contemporary works, since most of the composition rules in the Baroque period are wellknown and easily calculated, whereas the aesthetics of a romantic or contemporary work is harder to evaluate. Chorales and fugues are among the most common genres of Baroque compositions, and Bach, among other great composers of his time, has graced us with a wealth of excellent chorales and fugues that can used as the training dataset.

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
