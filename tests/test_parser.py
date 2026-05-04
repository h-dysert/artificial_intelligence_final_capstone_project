import pandas as pd

from app.parser import (
    get_choice_columns,
    validate_student_data,
    validate_project_data,
)


def test_get_choice_columns_returns_sorted_choices():
    df = pd.DataFrame({
        "student_id": [1],
        "student_name": ["Alice"],
        "choice_3": ["Project C"],
        "choice_1": ["Project A"],
        "choice_2": ["Project B"],
    })

    choice_columns = get_choice_columns(df)

    assert choice_columns == ["choice_1", "choice_2", "choice_3"]


def test_validate_student_data_accepts_valid_file():
    df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "choice_2": ["Mobile App", "Cybersecurity Tool", "AI Chatbot"],
    })

    is_valid, message = validate_student_data(df)

    assert is_valid is True
    assert message == "Student file looks valid."


def test_validate_student_data_rejects_missing_required_column():
    df = pd.DataFrame({
        "student_id": [1, 2],
        # Missing student_name
        "choice_1": ["AI Chatbot", "Mobile App"],
    })

    is_valid, message = validate_student_data(df)

    assert is_valid is False
    assert "missing required columns" in message
    assert "student_name" in message


def test_validate_student_data_rejects_duplicate_student_ids():
    df = pd.DataFrame({
        "student_id": [1, 1],
        "student_name": ["Alice", "Ben"],
        "choice_1": ["AI Chatbot", "Mobile App"],
    })

    is_valid, message = validate_student_data(df)

    assert is_valid is False
    assert message == "Student IDs must be unique."


def test_validate_project_data_accepts_valid_file():
    df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "min_students": [1, 1, 1],
        "max_students": [2, 3, 2],
    })

    is_valid, message = validate_project_data(df)

    assert is_valid is True
    assert message == "Project file looks valid."


def test_validate_project_data_rejects_missing_required_column():
    df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [1, 1],
        # Missing max_students
    })

    is_valid, message = validate_project_data(df)

    assert is_valid is False
    assert "missing required columns" in message
    assert "max_students" in message


def test_validate_project_data_rejects_duplicate_project_names():
    df = pd.DataFrame({
        "project_name": ["AI Chatbot", "AI Chatbot"],
        "min_students": [1, 1],
        "max_students": [2, 3],
    })

    is_valid, message = validate_project_data(df)

    assert is_valid is False
    assert message == "Project names must be unique."


def test_validate_project_data_rejects_negative_capacity():
    df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [1, -1],
        "max_students": [2, 3],
    })

    is_valid, message = validate_project_data(df)

    assert is_valid is False
    assert message == "Project capacities cannot be negative."


def test_validate_project_data_rejects_max_less_than_min():
    df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [3, 1],
        "max_students": [2, 3],
    })

    is_valid, message = validate_project_data(df)

    assert is_valid is False
    assert message == "Each project's max_students must be greater than or equal to min_students."