import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

def main_app():
    # Load the data (replace 'your_data.csv' with your actual file)
    @st.cache_data
    def load_data():
        return pd.read_csv("C:/Users/devar/Downloads/data.csv")

    data = load_data()

    # Ensure 'Student Name' and 'Advisor' columns exist
    if "Student Name" not in data.columns or "Advisor" not in data.columns:
        st.error("CSV file must include both 'Student Name' and 'Advisor' columns.")
    else:
        # Sort the students based on the "Advisor" column (alphabetically)
        sorted_data = data.sort_values(by="Advisor")
        
        # Sidebar: Select a student along with the advisor name
        # Combine Student Name and Advisor for display in dropdown
        student_advisor_list = sorted_data.apply(lambda row: f"{row['Student Name']} ({row['Advisor']})", axis=1).dropna().unique().tolist()
        student_advisor_list.insert(0, "")  # Add a blank option at the top
        selected_student_advisor = st.sidebar.selectbox("Select a Student", student_advisor_list)

        # Only proceed if a valid student-advisor pair is selected
        if selected_student_advisor:
            # Extract the student name from the combined string
            selected_student_name = selected_student_advisor.split(" (")[0]

            # Filter data for the selected student
            student_data = sorted_data[sorted_data["Student Name"] == selected_student_name].drop(columns=["Student Name", "Advisor"])

            # Exclude the "Advisor" column if present
            if student_data.shape[1] > 1:
                student_data = student_data.iloc[:, 1:]  # Drop the first remaining column
            
            # Drop columns where the student has no score
            student_data = student_data.dropna(axis=1)

            # Convert scores to numeric (if needed)
            student_data = student_data.apply(pd.to_numeric, errors="coerce")

            # Transpose data for better visualization
            student_data = student_data.T
            student_data.columns = ["Score"]  # Rename the column for clarity

            # Display results
            st.write(f"### Test Scores for {selected_student_name} (Advisor: {sorted_data.loc[sorted_data['Student Name'] == selected_student_name, 'Advisor'].values[0]})")

            # Plot with Matplotlib for label rotation
            if not student_data.empty:
                fig, ax = plt.subplots()
                bars = ax.bar(student_data.index, student_data["Score"], color="skyblue")

                # Add data labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}", 
                            ha="center", va="bottom", fontsize=10, fontweight="bold")

                # Trendline code, not sure if I want to include it
                # # Trendline (Linear Fit)
                # x = np.arange(len(student_data))  # Numeric indices for x-axis
                # y = student_data["Score"].values  # Scores as y-values

                # if len(x) > 1:  # Ensure there's enough data for a trendline
                #     z = np.polyfit(x, y, 1)  # Linear regression (degree=1)
                #     p = np.poly1d(z)  # Create polynomial function

                #     ax.plot(x, p(x), color="red", linestyle="--", linewidth=2, label="Trendline")

                # Rotate x-axis labels
                plt.xticks(rotation=45, ha="right")

                # Labels and title
                plt.xlabel("Test")
                plt.ylabel("Score")
                plt.title(f"Test Scores for {selected_student_name}")

                # Show legend
                ax.legend()

                # Display plot in Streamlit
                st.pyplot(fig)
            else:
                st.warning(f"No valid test scores available for {selected_student_name}.")

if st.session_state.authenticated:
    main_app()
else:
    login()
