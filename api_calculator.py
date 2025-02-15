import pandas as pd
import streamlit as st

def calculate_api(file):
    df = pd.read_excel(file)

    # Check if required columns exist
    if not {'Name', 'Marks'}.issubset(df.columns):
        st.error("Excel file must contain 'Name' and 'Marks' columns.")
        return

    # Define categories and weightage
    categories = {
        '>95': (95, 100, 10),
        '90-94.99': (90, 94.99, 8),
        '80-89.99': (80, 89.99, 6),
        '70-79.99': (70, 79.99, 4),
        '60-69.99': (60, 69.99, 2),
        '50-59.99': (50, 59.99, 0),
        '33-49.99': (33, 49.99, -1),
        '<33': (0, 32.99, -3),
    }

    # Count students in each category
    category_counts = {key: 0 for key in categories}
    for mark in df['Marks']:
        for category, (low, high, weight) in categories.items():
            if low <= mark <= high:
                category_counts[category] += 1
                break

    # Calculate API score
    total_weighted_score = sum(category_counts[cat] * weight for cat, (_, _, weight) in categories.items())
    total_students = len(df)

    if total_students == 0:
        st.error("No students found in the data.")
        return

    api_score = (total_weighted_score / total_students) * 100

    # Display results
    st.write("### API Calculation Results")
    st.write("Number of students in each category:")
    st.dataframe(pd.DataFrame({'Category': category_counts.keys(), 'Count': category_counts.values()}))
    st.write(f"### API Score: {api_score:.2f}")

# Streamlit UI
st.title("API Calculator for Student Marks")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    calculate_api(uploaded_file)
