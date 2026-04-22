# Reads and validates CSV input files

import pandas as pd


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