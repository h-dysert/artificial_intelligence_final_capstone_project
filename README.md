# Capstone Project Matcher

## Overview

Capstone Project Matcher is a Python application that helps the ECCS chair assign students to capstone projects based on ranked student preferences and project capacity limits.

Students submit their ranked project choices, and the application generates a recommended assignment that aims to maximize overall student satisfaction while respecting project size constraints.

## Problem

Assigning students to capstone projects by hand can be time-consuming and difficult, especially when many students want the same projects. This application provides a structured and data-driven way to support those assignment decisions.

## Features

- Upload student ranking data
- Upload project capacity data
- Validate uploaded CSV files
- Generate recommended student-to-project assignments
- Display project rosters
- Show summary statistics for preference satisfaction
- Export assignment results
- Run automated tests for the parser, scoring, and matching logic

## How It Works

The application reads:

1. A student rankings CSV file
2. A project capacities CSV file

It then:

- Validates the uploaded files
- Finds each student’s ranked project choices
- Converts rankings into weighted preference scores
- Builds a score matrix
- Assigns students to projects using an optimization-based matching algorithm
- Ensures project minimum and maximum capacity rules are respected
- Returns a recommended assignment for review

## Installation 
Step 1: Open the project folder in VS Code or your preferred editor.

Make sure you are in the project root folder. The project root should contain:

README.md
ROBOTS.md
app
data
requirements.txt
tests

Step 2: Create a virtual environment

On macOS or Linux:

python3.11 -m venv .venv

If you are using Windows:

python -m venv .venv

Step 3: Activate the virtual environment

On macOS or Linux:

source .venv/bin/activate

On Windows PowerShell:

.venv\Scripts\Activate.ps1

Step 4: Install required packages

python -m pip install -r requirements.txt

The requirements.txt file should contain only package names:

streamlit
pandas
numpy
scipy
pytest

Running the App

From the project root folder, run:

python -m streamlit run app/main.py

Or:

streamlit run app/main.py

The app should open in your browser at: http://localhost:8501 

Make sure you run the command from the project root folder, not from inside the app folder.

Correct from the project root: python -m streamlit run app/main.py

Incorrect from the project root:

streamlit run main.py (this will fail because main.py is inside the app folder.)

Running Tests

This project uses pytest for automated testing.

From the project root folder, run: python -m pytest

The tests are located in the tests folder:

tests/test_parser.py
tests/test_scoring.py
tests/test_matching.py

The tests check that:

Student CSV files are validated correctly
Project CSV files are validated correctly
Choice columns are detected and sorted correctly
Preference rankings are converted into scores correctly
The score matrix is built correctly
The matching problem is checked for feasibility
Assignments respect project capacity limits
Each student receives one assignment
Project rosters are built correctly
Satisfaction summaries are calculated correctly


## Project Structure

```text
capstone-project-matcher
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── parser.py
│   ├── scoring.py
│   ├── matching.py
│   └── utils.py
├── data
├── tests
│   ├── test_parser.py
│   ├── test_scoring.py
│   └── test_matching.py
├── README.md
├── ROBOTS.md
└── requirements.txt
