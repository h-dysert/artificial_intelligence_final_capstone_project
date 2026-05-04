import pandas as pd

from app.matching import (
    check_matching_feasibility,
    optimize_assignments,
    build_project_roster,
    calculate_satisfaction,
    calculate_total_capacity,
)


def test_check_matching_feasibility_accepts_valid_capacity():
    student_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [1, 1],
        "max_students": [2, 2],
    })

    is_feasible, error_message = check_matching_feasibility(student_df, project_df)

    assert is_feasible is True
    assert error_message is None


def test_check_matching_feasibility_rejects_not_enough_max_capacity():
    student_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [0, 0],
        "max_students": [1, 1],
    })

    is_feasible, error_message = check_matching_feasibility(student_df, project_df)

    assert is_feasible is False
    assert "Not enough total capacity" in error_message


def test_check_matching_feasibility_rejects_minimums_too_high():
    student_df = pd.DataFrame({
        "student_id": [1, 2],
        "student_name": ["Alice", "Ben"],
        "choice_1": ["AI Chatbot", "Mobile App"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App"],
        "min_students": [2, 2],
        "max_students": [3, 3],
    })

    is_feasible, error_message = check_matching_feasibility(student_df, project_df)

    assert is_feasible is False
    assert "Minimum project requirements are too high" in error_message


def test_optimize_assignments_returns_one_assignment_per_student():
    student_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "AI Chatbot", "Mobile App"],
        "choice_2": ["Mobile App", "Cybersecurity Tool", "AI Chatbot"],
        "choice_3": ["Cybersecurity Tool", "Mobile App", "Cybersecurity Tool"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "min_students": [0, 0, 0],
        "max_students": [1, 1, 1],
    })

    assignments_df, error_message = optimize_assignments(student_df, project_df)

    assert error_message is None
    assert assignments_df is not None
    assert len(assignments_df) == 3
    assert assignments_df["student_id"].nunique() == 3


def test_optimize_assignments_does_not_exceed_max_capacity():
    student_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "AI Chatbot", "AI Chatbot"],
        "choice_2": ["Mobile App", "Mobile App", "Mobile App"],
        "choice_3": ["Cybersecurity Tool", "Cybersecurity Tool", "Cybersecurity Tool"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "min_students": [0, 0, 0],
        "max_students": [1, 1, 1],
    })

    assignments_df, error_message = optimize_assignments(student_df, project_df)

    assert error_message is None

    assigned_counts = assignments_df["assigned_project"].value_counts().to_dict()

    for _, project in project_df.iterrows():
        project_name = project["project_name"]
        max_students = project["max_students"]

        assert assigned_counts.get(project_name, 0) <= max_students


def test_optimize_assignments_returns_error_when_infeasible():
    student_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
    })

    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot"],
        "min_students": [0],
        "max_students": [1],
    })

    assignments_df, error_message = optimize_assignments(student_df, project_df)

    assert assignments_df is None
    assert error_message is not None
    assert "Not enough total capacity" in error_message


def test_build_project_roster_groups_students_by_project():
    assignments_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "assigned_project": ["AI Chatbot", "AI Chatbot", "Mobile App"],
    })

    roster_df = build_project_roster(assignments_df)

    ai_roster = roster_df[
        roster_df["assigned_project"] == "AI Chatbot"
    ]["student_name"].iloc[0]

    assert ai_roster == ["Alice", "Ben"]


def test_calculate_satisfaction_counts_choice_results():
    student_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "choice_1": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "choice_2": ["Mobile App", "AI Chatbot", "Mobile App"],
    })

    assignments_df = pd.DataFrame({
        "student_id": [1, 2, 3],
        "student_name": ["Alice", "Ben", "Carla"],
        "assigned_project": ["AI Chatbot", "AI Chatbot", "Mobile App"],
    })

    satisfaction_df = calculate_satisfaction(assignments_df, student_df)

    results = dict(zip(satisfaction_df["Result"], satisfaction_df["Count"]))

    assert results["Choice 1"] == 1
    assert results["Choice 2"] == 2


def test_calculate_total_capacity_returns_sum_of_max_students():
    project_df = pd.DataFrame({
        "project_name": ["AI Chatbot", "Mobile App", "Cybersecurity Tool"],
        "min_students": [0, 1, 1],
        "max_students": [2, 3, 4],
    })

    total_capacity = calculate_total_capacity(project_df)

    assert total_capacity == 9