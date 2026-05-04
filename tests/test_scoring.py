import numpy as np
import pandas as pd

from app.scoring import build_score_matrix


def test_build_score_matrix_has_correct_shape():
    student_df = pd.DataFrame({
        "student_id": [1, 2],
        "student_name": ["Alice", "Ben"],
        "choice_1": ["AI Chatbot", "Mobile App"],
        "choice_2": ["Mobile App", "AI Chatbot"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [0, 0],
        "max_students": [2, 2],
    })

    score_matrix = build_score_matrix(student_df, project_df)

    assert score_matrix.shape == (2, 2)


def test_build_score_matrix_assigns_higher_score_to_first_choice():
    student_df = pd.DataFrame({
        "student_id": [1],
        "student_name": ["Alice"],
        "choice_1": ["AI Chatbot"],
        "choice_2": ["Mobile App"],
        "choice_3": ["Cybersecurity Tool"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "min_students": [0, 0, 0],
        "max_students": [1, 1, 1],
    })

    score_matrix = build_score_matrix(student_df, project_df)

    assert score_matrix[0, 0] == 3
    assert score_matrix[0, 1] == 2
    assert score_matrix[0, 2] == 1


def test_build_score_matrix_gives_zero_for_unranked_project():
    student_df = pd.DataFrame({
        "student_id": [1],
        "student_name": ["Alice"],
        "choice_1": ["AI Chatbot"],
        "choice_2": ["Mobile App"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "min_students": [0, 0, 0],
        "max_students": [1, 1, 1],
    })

    score_matrix = build_score_matrix(student_df, project_df)

    assert score_matrix[0, 0] == 2
    assert score_matrix[0, 1] == 1
    assert score_matrix[0, 2] == 0


def test_build_score_matrix_ignores_choice_that_is_not_valid_project():
    student_df = pd.DataFrame({
        "student_id": [1],
        "student_name": ["Alice"],
        "choice_1": ["Nonexistent Project"],
        "choice_2": ["AI Chatbot"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot"],
        "min_students": [0],
        "max_students": [1],
    })

    score_matrix = build_score_matrix(student_df, project_df)

    assert score_matrix[0, 0] == 1


def test_build_score_matrix_matches_expected_matrix():
    student_df = pd.DataFrame({
        "student_id": [1, 2],
        "student_name": ["Alice", "Ben"],
        "choice_1": ["AI Chatbot", "Mobile App"],
        "choice_2": ["Mobile App", "AI Chatbot"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [0, 0],
        "max_students": [2, 2],
    })

    score_matrix = build_score_matrix(student_df, project_df)

    expected = np.array([
        [2, 1],
        [1, 2],
    ])

    np.testing.assert_array_equal(score_matrix, expected)