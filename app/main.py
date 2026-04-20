# Runs the Streamlit app and handles UI

import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


def load_csv(uploaded_file):
    """Load an uploaded CSV file into a pandas DataFrame."""
    if uploaded_file is None:
        return None
    return pd.read_csv(uploaded_file)


def get_choice_columns(df):
    """Return sorted choice columns like choice_1, choice_2, ..."""
    choice_cols = [col for col in df.columns if col.startswith("choice_")]
    choice_cols.sort(key=lambda x: int(x.split("_")[1]))
    return choice_cols


def validate_student_data(df):
    """Validate the student rankings CSV."""
    required_columns = ["student_id", "student_name", "choice_1"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return False, f"Student file is missing required columns: {', '.join(missing)}"

    if df["student_id"].duplicated().any():
        return False, "Student IDs must be unique."

    choice_columns = get_choice_columns(df)
    if not choice_columns:
        return False, "Student file must include at least one choice column."

    return True, "Student file looks valid."


def validate_project_data(df):
    """Validate the project capacities CSV."""
    required_columns = ["project_name", "min_students", "max_students"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return False, f"Project file is missing required columns: {', '.join(missing)}"

    if df["project_name"].duplicated().any():
        return False, "Project names must be unique."

    if (df["min_students"] < 0).any() or (df["max_students"] < 0).any():
        return False, "Project capacities cannot be negative."

    if (df["max_students"] < df["min_students"]).any():
        return False, "Each project's max_students must be greater than or equal to min_students."

    return True, "Project file looks valid."


def build_score_matrix(student_df, project_df):
    """
    Build a score matrix where each cell is the satisfaction score for assigning
    a student to a project.
    """
    students = student_df.reset_index(drop=True)
    projects = project_df.reset_index(drop=True)
    choice_columns = get_choice_columns(student_df)

    num_students = len(students)
    num_projects = len(projects)

    score_matrix = np.zeros((num_students, num_projects), dtype=float)

    project_name_to_index = {
        row["project_name"]: idx for idx, row in projects.iterrows()
    }

    max_score = len(choice_columns)

    for student_idx, student in students.iterrows():
        for rank, choice_col in enumerate(choice_columns, start=1):
            project_name = student.get(choice_col)

            if pd.notna(project_name) and project_name in project_name_to_index:
                project_idx = project_name_to_index[project_name]
                score_matrix[student_idx, project_idx] = max_score - rank + 1

    return score_matrix


def optimize_assignments(student_df, project_df):
    """
    Solve the assignment problem using mixed-integer linear programming.

    Decision variable:
        x[i, j] = 1 if student i is assigned to project j, else 0

    Objective:
        maximize total satisfaction score

    Constraints:
        - each student assigned to exactly one project
        - each project assigned no more than max_students
    """
    students = student_df.reset_index(drop=True)
    projects = project_df.reset_index(drop=True)

    num_students = len(students)
    num_projects = len(projects)

    score_matrix = build_score_matrix(students, projects)

    # Flatten x[i, j] into a single vector
    num_variables = num_students * num_projects

    # scipy.optimize.milp minimizes, so negate scores to maximize satisfaction
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
        LinearConstraint(student_constraint_matrix,
                         lb=np.ones(num_students),
                         ub=np.ones(num_students))
    )

    # Constraint 2: each project cannot exceed max_students
    project_constraint_matrix = np.zeros((num_projects, num_variables))
    for j in range(num_projects):
        for i in range(num_students):
            project_constraint_matrix[j, i * num_projects + j] = 1

    max_caps = projects["max_students"].to_numpy(dtype=float)

    constraints.append(
        LinearConstraint(project_constraint_matrix,
                         lb=np.zeros(num_projects),
                         ub=max_caps)
    )

    result = milp(
        c=c,
        constraints=constraints,
        integrality=integrality,
        bounds=bounds
    )

    if not result.success or result.x is None:
        return None, "Optimization failed. Check whether total project capacity is enough for all students."

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
    merged = assignments_df.merge(student_df, on=["student_id", "student_name"], how="left")
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
    """Return total available max capacity."""
    return int(project_df["max_students"].sum())


st.set_page_config(page_title="Capstone Project Matcher", layout="wide")

st.title("Capstone Project Matcher")
st.write(
    "Upload a student rankings CSV and a project capacities CSV to generate "
    "optimized capstone project assignments."
)

st.header("Upload Input Files")

student_file = st.file_uploader("Upload student rankings CSV", type=["csv"])
project_file = st.file_uploader("Upload project capacities CSV", type=["csv"])

student_df = None
project_df = None

if student_file is not None:
    student_df = load_csv(student_file)
    valid_students, student_message = validate_student_data(student_df)

    if valid_students:
        st.success(student_message)
        st.subheader("Student Rankings Preview")
        st.dataframe(student_df)
    else:
        st.error(student_message)

if project_file is not None:
    project_df = load_csv(project_file)
    valid_projects, project_message = validate_project_data(project_df)

    if valid_projects:
        st.success(project_message)
        st.subheader("Project Capacities Preview")
        st.dataframe(project_df)
    else:
        st.error(project_message)

st.header("Run Optimization")

if st.button("Generate Optimized Assignments"):
    if student_df is None or project_df is None:
        st.error("Please upload both CSV files first.")
    else:
        valid_students, student_message = validate_student_data(student_df)
        valid_projects, project_message = validate_project_data(project_df)

        if not valid_students:
            st.error(student_message)
        elif not valid_projects:
            st.error(project_message)
        else:
            total_students = len(student_df)
            total_capacity = calculate_total_capacity(project_df)

            if total_capacity < total_students:
                st.error(
                    f"Not enough total capacity. There are {total_students} students "
                    f"but only {total_capacity} available project slots."
                )
            else:
                assignments_df, error_message = optimize_assignments(student_df, project_df)

                if error_message:
                    st.error(error_message)
                else:
                    roster_df = build_project_roster(assignments_df)
                    satisfaction_df = calculate_satisfaction(assignments_df, student_df)

                    st.subheader("Student Assignments")
                    st.dataframe(assignments_df)

                    st.subheader("Project Rosters")
                    st.dataframe(roster_df)

                    st.subheader("Preference Satisfaction Summary")
                    st.dataframe(satisfaction_df)

                    csv_output = assignments_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download Assignments CSV",
                        data=csv_output,
                        file_name="capstone_assignments.csv",
                        mime="text/csv",
                    )