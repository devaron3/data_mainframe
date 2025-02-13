import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to load CSV file
def load_csv(file):
    if file:
        return pd.read_csv(file), file.name.replace(".csv", "")
    return None, None

# Sidebar: Upload files
st.sidebar.header("Upload CSV Files")
uploaded_file1 = st.sidebar.file_uploader("Upload First Dataset", type=["csv"])
uploaded_file2 = st.sidebar.file_uploader("Upload Second Dataset", type=["csv"])
uploaded_file3 = st.sidebar.file_uploader("Upload Third Dataset", type=["csv"])

# Load datasets
data1, filename1 = load_csv(uploaded_file1)
data2, filename2 = load_csv(uploaded_file2)
data3, filename3 = load_csv(uploaded_file3)

# Set default filenames
filename1 = filename1 if filename1 else "First Dataset"
filename2 = filename2 if filename2 else "Second Dataset"
filename3 = filename3 if filename3 else "Third Dataset"

# Check if at least one dataset is uploaded
if data1 is None and data2 is None and data3 is None:
    st.warning("Please upload at least one dataset.")
    st.stop()

# Function to process student list
def extract_students(data):
    if data is not None and "Student Name" in data.columns and "Advisor" in data.columns:
        return [(row["Student Name"], row["Advisor"]) for _, row in data[["Student Name", "Advisor"]].dropna().iterrows()]
    return []

# Combine and sort student lists by Advisor
student_list1 = extract_students(data1)
student_list2 = extract_students(data2)
student_list3 = extract_students(data3)

# Fix: Use a set of tuples (not lists) to remove duplicates
student_list = sorted(set(student_list1 + student_list2 + student_list3), key=lambda x: x[1])

# Format student dropdown: "John Doe (Ms. Smith)"
formatted_students = [f"{name} ({adv})" for name, adv in student_list if name]
formatted_students.insert(0, "")  # Blank option

# Sidebar: Select a student
selected_student = st.sidebar.selectbox("Select a Student", formatted_students)

# Extract actual student name (before the advisor part)
selected_student = selected_student.split(" (")[0] if selected_student else None

# Function to process student data
def process_student_data(data, student_name):
    if data is None or "Student Name" not in data.columns or student_name not in data["Student Name"].values:
        return None
    student_data = data[data["Student Name"] == student_name].drop(columns=["Student Name", "Advisor"], errors="ignore")

    if student_data.shape[1] > 1:
        student_data = student_data.iloc[:, 1:]  

    student_data = student_data.dropna(axis=1).T
    student_data.columns = ["Score"]
    return student_data.apply(pd.to_numeric, errors="coerce")

# Function to create bar chart
def plot_chart(student_data, filename):
    if student_data is not None and not student_data.empty:
        fig, ax = plt.subplots()
        bars = ax.bar(student_data.index, student_data["Score"], color="skyblue")

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}", 
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

        x = np.arange(len(student_data))
        y = student_data["Score"].values
        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            ax.plot(x, p(x), color="red", linestyle="--", linewidth=2, label="Trendline")

        plt.xticks(rotation=45, ha="right")
        # plt.xlabel(f"{filename}")
        plt.ylabel(f"{filename} Score")
        # plt.title(f"Scores for {selected_student} ({filename})")
        ax.legend()
        st.pyplot(fig)

# Display charts
if selected_student:
    st.write(f"### Score Analysis for {selected_student}")

    student_data1 = process_student_data(data1, selected_student)
    student_data2 = process_student_data(data2, selected_student)
    student_data3 = process_student_data(data3, selected_student)

    if student_data1 is not None:
        plot_chart(student_data1, filename1)
    else:
        st.warning(f"No scores available for {selected_student} in {filename1}.")

    if student_data2 is not None:
        plot_chart(student_data2, filename2)
    else:
        st.warning(f"No scores available for {selected_student} in {filename2}.")

    if student_data3 is not None:
        plot_chart(student_data3, filename3)
    else:
        st.warning(f"No scores available for {selected_student} in {filename3}.")
