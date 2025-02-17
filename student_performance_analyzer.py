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
    category_students = {key: [] for key in categories}
    
    for _, row in df.iterrows():
        mark = row['Marks']
        for category, (low, high, weight) in categories.items():
            if low <= mark <= high:
                category_counts[category] += 1
                category_students[category].append(row['Name'])
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
    breakdown_df = pd.DataFrame({'Category': category_counts.keys(), 'Count': category_counts.values()})
    st.dataframe(breakdown_df)
    st.write(f"### API Score: {api_score:.2f}")

    # Display students categorized by division
    st.write("### Students Categorized by Division")
    for category, students in category_students.items():
        st.write(f"#### {category} ({len(students)} students)")
        st.write(", ".join(students) if students else "No students in this category")

def compare_assessments(files):
    all_data = []
    
    for file in files:
        df = pd.read_excel(file)
        if not {'Name', 'Marks'}.issubset(df.columns):
            st.error(f"Excel file {file.name} must contain 'Name' and 'Marks' columns.")
            return None
        df['Assessment'] = file.name  # Store assessment name
        all_data.append(df[['Name', 'Marks', 'Assessment']])
    
    if not all_data:
        return None
    
    df_combined = pd.concat(all_data)
    df_avg = df_combined.groupby('Name')['Marks'].mean().reset_index()
    df_avg['Category'] = pd.cut(
        df_avg['Marks'],
        bins=[0, 49.99, 59.99, 69.99, 79.99, 100],
        labels=["Remedial", "Scope to Become Average", "Average", "Scope to Become High Achiever", "High Achiever"]
    )
    return df_avg

# Streamlit UI
st.title("API Calculator and Comparative Analysis")
option = st.radio("Choose Analysis Type:", ("Simple API Calculation", "Comparative Analysis"))

if option == "Simple API Calculation":
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file:
        calculate_api(uploaded_file)
else:
    uploaded_files = st.file_uploader("Upload Multiple Assessment Files", type=["xlsx"], accept_multiple_files=True)
    if uploaded_files:
        comparison_df = compare_assessments(uploaded_files)
        if comparison_df is not None:
            st.write("### Comparative Assessment Report")
            st.dataframe(comparison_df)
            # Allow download of the report
            csv = comparison_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Report", csv, "comparative_analysis_report.csv", "text/csv")
