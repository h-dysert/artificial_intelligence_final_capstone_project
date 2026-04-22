# Contains the assignement algorithm

"""Matching and reporting logic for capstone project assignments."""

import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

from scoring import build_score_matrix
from parser import get_choice_columns


def check_matching_feasibility(student_df, project_df):
    """
    Check whether the assignment problem is feasible before optimization.

    Conditions:
    - Total max capacity must be at least the number of students.
    - Total min capacity must be at most the number of students.

    Returns:
        (is_feasible, error_message)
    """
    total_students = len(student_df)
    total_min = int(project_df["min_students"].sum())
    total_max = int(project_df["max_students"].sum())

    if total_max < total_students:
        return (
            False,
            f"Not enough total capacity. There are {total_students} students "
            f"but only {total_max} available project slots.",
        )

    if total_min > total_students:
        return (
            False,
            f"Minimum project requirements are too high. Projects require at least "
            f"{total_min} total students, but only {total_students} students are available.",
        )

    return True, None


def optimize_assignments(student_df, project_df):
    """
    Solve the assignment problem using mixed-integer linear programming.

    Decision variable:
        x[i, j] = 1 if student i is assigned to project j, else 0

    Objective:
        maximize total satisfaction score

    Constraints:
        - each student assigned to exactly one project
        - each project assigned at least min_students
        - each project assigned at most max_students

    Returns:
        (assignments_df, error_message)
    """
    students = student_df.reset_index(drop=True)
    projects = project_df.reset_index(drop=True)

    feasible, error_message = check_matching_feasibility(students, projects)
    if not feasible:
        return None, error_message

    num_students = len(students)
    num_projects = len(projects)

    score_matrix = build_score_matrix(students, projects)

    # Flatten x[i, j] into one vector of length num_students * num_projects
    num_variables = num_students * num_projects

    # scipy.optimize.milp minimizes, so negate to maximize preference score
    c = -score_matrix.flatten()

    integrality = np.ones(num_variables, dtype=int)
    bounds = Bounds(lb=np.zeros(num_variables), ub=np.ones(num_variables))

    constraints = []

    # Constraint 1: each student gets exactly one project
    student_constraint_matrix = np.zeros((num_students, num_variables))
    for i in range(num_students):
        for j in range(num_projects):
            student_constraint_matrix[i, i * num_projects + j] = 1

    constraints.append(
        LinearConstraint(
            student_constraint_matrix,
            lb=np.ones(num_students),
            ub=np.ones(num_students),
        )
    )

    # Constraint 2: each project must satisfy min_students <= assigned <= max_students
    project_constraint_matrix = np.zeros((num_projects, num_variables))
    for j in range(num_projects):
        for i in range(num_students):
            project_constraint_matrix[j, i * num_projects + j] = 1

    min_caps = projects["min_students"].to_numpy(dtype=float)
    max_caps = projects["max_students"].to_numpy(dtype=float)

    constraints.append(
        LinearConstraint(
            project_constraint_matrix,
            lb=min_caps,
            ub=max_caps,
        )
    )

    result = milp(
        c=c,
        constraints=constraints,
        integrality=integrality,
        bounds=bounds,
    )

    if not result.success or result.x is None:
        return None, (
            "Optimization failed. The project minimum/maximum capacity rules and "
            "student preferences may not produce a feasible assignment."
        )

    solution = result.x.reshape((num_students, num_projects))

    assignments = []
    for i in range(num_students):
        assigned_project = "Unassigned"

        for j in range(num_projects):
            if solution[i, j] > 0.5:
                assigned_project = projects.loc[j, "project_name"]
                break

        assignments.append(
            {
                "student_id": students.loc[i, "student_id"],
                "student_name": students.loc[i, "student_name"],
                "assigned_project": assigned_project,
            }
        )

    return pd.DataFrame(assignments), None


def build_project_roster(assignments_df):
    """Group students by assigned project."""
    roster = (
        assignments_df.groupby("assigned_project")["student_name"]
        .apply(list)
        .reset_index()
    )
    return roster


def calculate_satisfaction(assignments_df, student_df):
    """Calculate how many students received each choice rank."""
    merged = assignments_df.merge(
        student_df,
        on=["student_id", "student_name"],
        how="left",
    )
    choice_columns = get_choice_columns(student_df)

    results = []

    for _, row in merged.iterrows():
        assigned = row["assigned_project"]
        rank_received = "Unassigned"

        for index, choice_col in enumerate(choice_columns, start=1):
            if row.get(choice_col) == assigned:
                rank_received = f"Choice {index}"
                break

        results.append(rank_received)

    summary = pd.Series(results).value_counts().reset_index()
    summary.columns = ["Result", "Count"]
    return summary


def calculate_total_capacity(project_df):
    """Return total available maximum capacity."""
    return int(project_df["max_students"].sum())