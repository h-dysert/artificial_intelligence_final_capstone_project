# ROBOTS.md

## Project Purpose
This project matches students to capstone projects using ranked preferences and project capacity constraints.

## Architecture
- app/main.py handles the user interface
- app/parser.py reads and validates uploaded CSV files
- app/scoring.py converts rankings into preference scores
- app/matching.py computes optimized project assignments
- tests/contains automated tests for validation, scoring, and matching

## AI Agent Rules
- Keep UI logic separate from matching logic
- Never place optimization code inside the interface file
- Add or update tests whenever matching behavior changes
- Preserve clear comments and docstrings
- Favor readable, modular functions over long scripts

## Data Expectations
- Student file must include unique IDs and ranked project preferences
- Project file must include project names and capacity limits