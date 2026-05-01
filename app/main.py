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

st.set_page_config(
    page_title="Capstone Project Matcher",
    page_icon="🎓",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #eef4ff;
        --surface: #ffffff;
        --text: #0f172a;
        --muted: #475569;
        --accent: #2563eb;
        --accent-soft: #dbeafe;
        --success: #16a34a;
        --danger: #dc2626;
    }

    body {
        background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
    }

    .stApp {
        color: var(--text);
    }

    .page-header {
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        box-shadow: 0 20px 50px rgba(37, 99, 235, 0.14);
    }

    .section-card {
        background: var(--surface);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
        margin-bottom: 24px;
    }

    .section-card h2,
    .section-card h3 {
        color: var(--text);
    }

    .stButton>button {
        background: var(--accent);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 12px 28px;
        font-weight: 600;
    }

    .stButton>button:hover {
        background: #1d4ed8;
    }

    .upload-label {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 8px;
        display: block;
    }

    .hint {
        color: var(--muted);
        margin-top: 8px;
    }

    .info-panel {
        background: #f8fafc;
        border-left: 4px solid var(--accent);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 24px;
    }

    .info-panel strong {
        color: var(--text);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='page-header'>
        <h1>Capstone Project Matcher</h1>
        <p style='font-size:1.1rem;line-height:1.8rem;margin-top:10px;'>
            Upload student rankings and project capacity files, then generate optimized
            assignments using a clean, modern matching workflow.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container():
    left, right = st.columns([2, 1])

    with left:
        st.markdown("""
            <div class='section-card'>
                <h2>Upload Input Files</h2>
                <p class='hint'>Start with the student ranking CSV and project capacity CSV. The app validates each file automatically.</p>
            </div>
        """, unsafe_allow_html=True)

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

        st.markdown("""
            <div class='section-card'>
                <h2>Run Optimization</h2>
                <p class='hint'>Once both inputs are loaded and valid, generate the best possible assignments.</p>
            </div>
        """, unsafe_allow_html=True)

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

                            st.markdown("""
                                <div class='section-card'>
                                    <h3>Student Assignments</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            st.dataframe(assignments_df)

                            st.markdown("""
                                <div class='section-card'>
                                    <h3>Project Rosters</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            st.dataframe(roster_df)

                            st.markdown("""
                                <div class='section-card'>
                                    <h3>Preference Satisfaction Summary</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            st.dataframe(satisfaction_df)

                            csv_output = assignments_df.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                label="Download Assignments CSV",
                                data=csv_output,
                                file_name="capstone_assignments.csv",
                                mime="text/csv",
                            )

    with right:
        st.markdown("""
            <div class='info-panel'>
                <h3>How to use</h3>
                <ul style='padding-left:18px;margin-top:10px;'>
                    <li>Upload student ranking and project capacity CSVs.</li>
                    <li>Confirm both files validate successfully.</li>
                    <li>Click the button to generate assignments.</li>
                    <li>Review summaries and download the results.</li>
                </ul>
                <p class='hint'>Use the CSV preview to verify your column names and ranking order.</p>
            </div>
            <div class='info-panel'>
                <h3>Quick tips</h3>
                <p><strong>student_id</strong>, <strong>student_name</strong>, and ranked choices are required.</p>
                <p><strong>project_name</strong>, <strong>min_students</strong>, <strong>max_students</strong> are required.</p>
            </div>
        """, unsafe_allow_html=True)
