import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO

def calculate_simple_api(file):
    df = pd.read_excel(file)
    if not {'Name', 'Marks'}.issubset(df.columns):
        st.error("Excel file must contain 'Name' and 'Marks' columns.")
        return
    
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
    
    category_counts = {key: 0 for key in categories}
    for _, row in df.iterrows():
        mark = row['Marks']
        for category, (low, high, weight) in categories.items():
            if low <= mark <= high:
                category_counts[category] += 1
                break
    
    total_students = len(df)
    if total_students == 0:
        st.error("No students found in the data.")
        return
    
    total_weighted_score = sum(category_counts[cat] * weight for cat, (_, _, weight) in categories.items())
    api_score = (total_weighted_score / total_students) * 100
    
    st.write("### Simple API Calculation Results")
    breakdown_df = pd.DataFrame({'Category': category_counts.keys(), 'Count': category_counts.values()})
    st.dataframe(breakdown_df)
    st.write(f"### API Score: {api_score:.2f}")

def compare_assessments(files):
    all_data = []
    for file in files:
        df = pd.read_excel(file)
        if not {'Name', 'Marks'}.issubset(df.columns):
            st.error(f"Excel file {file.name} must contain 'Name' and 'Marks' columns.")
            return None
        df['Assessment'] = file.name
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
    
    st.write("### Comparative Assessment Report")
    for category in df_avg['Category'].unique():
        category_df = df_avg[df_avg['Category'] == category]
        st.write(f"#### {category} ({len(category_df)} students)")
        st.dataframe(category_df)
    
    csv = df_avg.to_csv(index=False).encode('utf-8')
    st.download_button("Download Full Report", csv, "comparative_analysis_report.csv", "text/csv")

def calculate_overall_api(file):
    df = pd.read_excel(file)
    subject_columns = ['English', 'Hindi', 'Maths', 'Science', 'SST', 'Sanskrit']
    
    if not all(sub in df.columns for sub in subject_columns):
        st.error("Excel file must contain all required subjects: English, Hindi, Maths, Science, SST, Sanskrit.")
        return
    
    df['Total Marks'] = df[subject_columns].sum(axis=1)
    df['Percentage'] = (df['Total Marks'] / (len(subject_columns) * 100)) * 100
    
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
    
    category_counts = {key: 0 for key in categories}
    feedback_messages = []
    
    for _, row in df.iterrows():
        mark = row['Percentage']
        for category, (low, high, weight) in categories.items():
            if low <= mark <= high:
                category_counts[category] += 1
                break
        
        if mark >= 90:
            feedback_messages.append("Excellent performance")
        elif mark >= 75:
            feedback_messages.append("Good performance, keep improving")
        elif mark >= 60:
            feedback_messages.append("Needs some improvement")
        elif mark >= 33:
            feedback_messages.append("Needs significant improvement")
        else:
            feedback_messages.append("At risk, requires immediate attention")
    
    df['Feedback'] = feedback_messages
    
    total_weighted_score = sum(category_counts[cat] * weight for cat, (_, _, weight) in categories.items())
    total_students = len(df)
    
    if total_students == 0:
        st.error("No students found in the data.")
        return
    
    api_score = (total_weighted_score / total_students) * 100
    
    st.write("### Overall Class API Calculation Results")
    breakdown_df = pd.DataFrame({'Category': category_counts.keys(), 'Count': category_counts.values()})
    st.dataframe(breakdown_df)
    st.write(f"### API Score: {api_score:.2f}")
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Student Scores', index=False)
        writer._save()
    
    st.download_button(
        label="Download Excel Report",
        data=output.getvalue(),
        file_name="class_api_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
