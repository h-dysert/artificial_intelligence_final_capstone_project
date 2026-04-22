import streamlit as st

from parser import (
    load_csv,
    validate_student_data,
    validate_project_data,
)
from matching import (
    check_matching_feasibility,
    optimize_assignments,
    build_project_roster,
    calculate_satisfaction,
)

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
            feasible, feasibility_message = check_matching_feasibility(
                student_df,
                project_df,
            )

            if not feasible:
                st.error(feasibility_message)
            else:
                assignments_df, error_message = optimize_assignments(
                    student_df,
                    project_df,
                )

                if error_message:
                    st.error(error_message)
                else:
                    roster_df = build_project_roster(assignments_df)
                    satisfaction_df = calculate_satisfaction(
                        assignments_df,
                        student_df,
                    )

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