# Converts rankings into numeric scores

import numpy as np
import pandas as pd
from parser import get_choice_columns


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