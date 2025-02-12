import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Authentication Check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("Login")
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == "PPHS2024":  # Replace with your password
            st.session_state.authenticated = True
            st.success("Access granted!")
        else:
            st.error("Access denied. Try again.")

def plot_scores(student_scores, title):
    """Helper function to plot student scores."""
    if not student_scores.empty:
        fig, ax = plt.subplots()
        bars = ax.bar(student_scores.index, student_scores["Score"], color="skyblue")

        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}", ha="center", va="bottom")

        # Trendline
        x = np.arange(len(student_scores))
        y = student_scores["Score"].values

        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            ax.plot(x, p(x), color="red", linestyle="--", linewidth=2, label="Trendline")

        plt.xticks(rotation=45, ha="right")
        plt.xlabel("Test")
        plt.ylabel("Score")
        plt.title(title)
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning(f"No valid test scores available for {title}.")

def main_app():
    st.title("Student Test Score Analysis")

    # Upload CSV Files
    file1 = st.sidebar.file_uploader("Upload First Test Score CSV", type=["csv"])
    file2 = st.sidebar.file_uploader("Upload Second Test Score CSV", type=["csv"])

    if not file1 and not file2:
        st.warning("Please upload at least one CSV file to continue.")
        return

    # Load DataFrames
    scores1 = pd.read_csv(file1) if file1 else None
    scores2 = pd.read_csv(file2) if file2 else None

    # Ensure required columns exist
    if scores1 is not None and "Student Name" not in scores1.columns:
        st.error("The first CSV must include a 'Student Name' column.")
        return
    if scores2 is not None and "Student Name" not in scores2.columns:
        st.error("The second CSV must include a 'Student Name' column.")
        return

    # Use the first dataset for student list (if available)
    if scores1 is not None and "Advisor" in scores1.columns:
        student_list = scores1[["Student Name", "Advisor"]].dropna().sort_values(by="Advisor").values.tolist()
    elif scores2 is not None and "Advisor" in scores2.columns:
        student_list = scores2[["Student Name", "Advisor"]].dropna().sort_values(by="Advisor").values.tolist()
    else:
        student_list = (scores1 or scores2)["Student Name"].dropna().unique().tolist()

    # Sidebar: Select a student (sorted by advisor)
    student_list = [("", "")] + student_list  # Add a blank option
    formatted_students = [f"{name} ({adv})" for name, adv in student_list if name]

    selected_student = st.sidebar.selectbox(
        "Select a Student",
        options=formatted_students
    )

    # Extract the actual student name from the formatted string
    selected_student = selected_student.split(" (")[0] if selected_student else ""


    if selected_student:
        # Display scores from the first dataset (if uploaded)
        if scores1 is not None:
            student_scores1 = scores1[scores1["Student Name"] == selected_student].drop(columns=["Student Name", "Advisor"], errors="ignore")
            if student_scores1.shape[1] > 1:
                student_scores1 = student_scores1.iloc[:, 1:].dropna(axis=1)

            student_scores1 = student_scores1.apply(pd.to_numeric, errors="coerce").T
            student_scores1.columns = ["Score"]

            st.write(f"### Test Scores for {selected_student} (First Dataset)")
            plot_scores(student_scores1, f"Test Scores for {selected_student} (First Dataset)")

        # Display scores from the second dataset (if uploaded)
        if scores2 is not None:
            student_scores2 = scores2[scores2["Student Name"] == selected_student].drop(columns=["Student Name", "Advisor"], errors="ignore")
            if student_scores2.shape[1] > 1:
                student_scores2 = student_scores2.iloc[:, 1:].dropna(axis=1)

            student_scores2 = student_scores2.apply(pd.to_numeric, errors="coerce").T
            student_scores2.columns = ["Score"]

            st.write(f"### Test Scores for {selected_student} (Second Dataset)")
            plot_scores(student_scores2, f"Test Scores for {selected_student} (Second Dataset)")

if st.session_state.authenticated:
    main_app()
else:
    login()
