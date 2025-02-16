import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def process_multiple_files(uploaded_files):
    all_data = []
    
    for file in uploaded_files:
        df = pd.read_excel(file)
        
        # Check for required columns
        if 'Name' not in df.columns:
            st.error(f"Error: {file.name} does not contain a 'Name' column.")
            return None
        
        # Identify mark columns
        mark_columns = [col for col in df.columns if col != 'Name']
        if len(mark_columns) == 1:
            df['Total Marks'] = df[mark_columns[0]]  # Use single column directly
        else:
            df['Total Marks'] = df[mark_columns].sum(axis=1)  # Sum if multiple columns exist
        
        df['Percentage'] = (df['Total Marks'] / df['Total Marks'].max()) * 100
        df['Assessment'] = file.name  # Add assessment name
        all_data.append(df[['Name', 'Percentage', 'Assessment']])

    return pd.concat(all_data)  # Combine all data

def calculate_api(df):
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
    for mark in df['Percentage']:
        for category, (low, high, weight) in categories.items():
            if low <= mark <= high:
                category_counts[category] += 1
                break
    total_weighted_score = sum(category_counts[cat] * weight for cat, (_, _, weight) in categories.items())
    total_students = len(df)
    return (total_weighted_score / total_students) * 100 if total_students > 0 else 0

def categorize_students(df):
    student_avg = df.groupby('Name')['Percentage'].mean().reset_index()
    student_avg['Category'] = pd.cut(
        student_avg['Percentage'],
        bins=[0, 49.99, 59.99, 69.99, 79.99, 100],
        labels=["Remedial", "Scope to Become Average", "Average", "Scope to Become High Achiever", "High Achiever"]
    )
    return student_avg

def generate_feedback(df):
    feedback = {
        "High Achiever": "Excellent performance! Keep it up! 🎉",
        "Scope to Become High Achiever": "You're close to excellence, push a little more! 🚀",
        "Average": "Good effort! Keep practicing to reach the top. 📈",
        "Scope to Become Average": "You're improving! Keep working hard! 💪",
        "Remedial": "Need focused improvement. Seek additional support. 📚"
    }
    df['Feedback'] = df['Category'].map(feedback)
    return df

def plot_student_progress(df):
    plt.figure(figsize=(12, 6))
    for name, group in df.groupby('Name'):
        plt.plot(group['Assessment'], group['Percentage'], marker='o', label=name, linestyle='-', linewidth=2)
    plt.xlabel("Assessment", fontsize=12)
    plt.ylabel("Percentage", fontsize=12)
    plt.title("Student Progress Over Assessments", fontsize=14, fontweight='bold')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(plt)

st.title("📊 Student Performance Analysis")
option = st.radio("Choose Analysis Type:", ("Simple API Calculation", "Comparative Analysis"))

uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    df = process_multiple_files(uploaded_files)

    if df is not None:
        if option == "Simple API Calculation":
            api_score = calculate_api(df)
            st.write(f"### 📊 API Score: {api_score:.2f}")
        else:
            categorized_df = categorize_students(df)
            final_df = generate_feedback(categorized_df)
            st.write("### 🏆 Student Performance Report")
            st.dataframe(final_df)
            
            # Detailed category-wise table
            st.write("### 📊 Detailed Student Categorization")
            for category in final_df['Category'].unique():
                st.write(f"#### {category}")
                st.dataframe(final_df[final_df['Category'] == category][['Name', 'Percentage', 'Feedback']])
            
            st.write("### 📈 Student Progress Visualization")
            plot_student_progress(df)
