# Capstone Project Matcher

## Overview
Capstone Project Matcher is a Python application that helps the ECCS chair assign students to capstone projects based on ranked student preferences and project capacity limits.

Students submit their ranked project choices, and the application generates a recommended assignment that aims to maximize overall student satisfaction while respecting project size constraints.

## Problem
Assigning students to capstone projects by hand can be time-consuming and difficult, especially when many students want the same projects. This application provides a structured and data-driven way to support those assignment decisions.

## Features
- Upload student ranking data
- Upload project capacity data
- Generate recommended student-to-project assignments
- Display project rosters
- Show summary statistics for preference satisfaction
- Export assignment results

## How It Works
The application reads:
1. A student rankings CSV file
2. A project capacities CSV file

It then:
- converts student rankings into weighted preference scores
- assigns students to projects using a matching algorithm
- ensures project capacities are not exceeded
- returns a recommended assignment for review

## Input Files

### Student Rankings CSV
The student rankings file must contain:
- `student_id`
- `student_name`
- ranked project choices such as `choice_1`, `choice_2`, `choice_3`, etc.

### Project Capacities CSV
The project capacities file must contain:
- `project_name`
- `min_students`
- `max_students`

## Example Student Rankings CSV
```csv
student_id,student_name,choice_1,choice_2,choice_3,choice_4,choice_5
1,Alex Johnson,AI Tutor,Schedule Optimizer,Note Scanner,Capstone Tracker,Lab Assistant Tool
2,Bri Thomas,Schedule Optimizer,AI Tutor,Capstone Tracker,Lab Assistant Tool,Note Scanner
3,Chris Lee,AI Tutor,Note Scanner,Schedule Optimizer,Lab Assistant Tool,Capstone Tracker
