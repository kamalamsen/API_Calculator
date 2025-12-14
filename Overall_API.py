import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO

# -------------------- COMMON UTILITIES --------------------
def normalize_headers(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

# -------------------- SIMPLE API (5 SUBJECTS) --------------------
def calculate_simple_api(file):
    df = pd.read_excel(file)
    df = normalize_headers(df)

    subject_columns = ['subject1', 'subject2', 'subject3', 'subject4', 'subject5']
    name_col = 'name' if 'name' in df.columns else None

    if not all(sub in df.columns for sub in subject_columns):
        st.error("Required columns missing. Please use the provided Excel template.")
        return

    # Validate marks
    for col in subject_columns:
        if df[col].max() > 100 or df[col].min() < 0:
            st.error("Marks must be between 0 and 100.")
            return

    df['total marks'] = df[subject_columns].sum(axis=1)
    df['percentage'] = (df['total marks'] / 500) * 100

    categories = [
        (95, 100, 10, 'High Achiever'),
        (90, 94.99, 8, 'High Achiever'),
        (80, 89.99, 6, 'Above Average'),
        (70, 79.99, 4, 'Average'),
        (60, 69.99, 2, 'Below Average'),
        (50, 59.99, 0, 'Needs Improvement'),
        (33, 49.99, -1, 'Remedial'),
        (0, 32.99, -3, 'Critical'),
    ]

    category_counts = {}
    performance_tags = []
    total_weighted_score = 0

    for pct in df['percentage']:
        for low, high, weight, tag in categories:
            if low <= pct <= high:
                total_weighted_score += weight
                category_counts[tag] = category_counts.get(tag, 0) + 1
                performance_tags.append(tag)
                break

    df['performance category'] = performance_tags
    df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)

    total_students = len(df)
    api_score = (total_weighted_score / total_students) * 100

    st.subheader("5-Subject API Result")
    st.dataframe(df)

    st.write(f"Class API Score: {api_score:.2f}")
    st.dataframe(pd.DataFrame(category_counts.items(), columns=['Category', 'Count']))

    # Download final Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Processed Data', index=False)
        pd.DataFrame({'API Score': [api_score], 'Total Students': [total_students]}).to_excel(writer, sheet_name='Summary', index=False)

    st.download_button(
        "Download Final Excel (Processed)",
        output.getvalue(),
        "API_5_Subjects_Final.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------- OVERALL CLASS API (6 SUBJECTS) --------------------
def calculate_overall_api(file):
    df = pd.read_excel(file)
    df = normalize_headers(df)

    subject_columns = ['english', 'hindi', 'maths', 'science', 'sst', 'sanskrit']
    if not all(sub in df.columns for sub in subject_columns):
        st.error("Required subject columns missing. Please use correct template.")
        return

    df['total marks'] = df[subject_columns].sum(axis=1)
    df['percentage'] = (df['total marks'] / (len(subject_columns) * 100)) * 100

    api_score = df['percentage'].mean()

    st.subheader("Overall Class API")
    st.write(f"Overall API Score: {api_score:.2f}")

    avg_scores = df[subject_columns].mean().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    avg_scores.plot(kind='bar')
    plt.title('Subject-wise Average')
    plt.ylabel('Average Marks')
    st.pyplot(plt)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Student Data', index=False)
        pd.DataFrame({'Overall API': [api_score]}).to_excel(writer, sheet_name='Summary', index=False)

    st.download_button(
        "Download Overall API Excel",
        output.getvalue(),
        "Overall_Class_API.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------- COMPARATIVE ANALYSIS --------------------
def compare_assessments(files):
    all_data = []
    for file in files:
        df = pd.read_excel(file)
        df = normalize_headers(df)
        if not {'name', 'marks'}.issubset(df.columns):
            st.error(f"{file.name} has invalid format")
            return
        df['assessment'] = file.name
        all_data.append(df[['name', 'marks', 'assessment']])

    df_all = pd.concat(all_data)
    df_avg = df_all.groupby('name')['marks'].mean().reset_index()
    df_avg['category'] = pd.cut(
        df_avg['marks'],
        bins=[0, 49.99, 59.99, 69.99, 79.99, 100],
        labels=['Remedial', 'Needs Improvement', 'Average', 'Above Average', 'High Achiever']
    )

    st.subheader("Comparative Assessment Result")
    st.dataframe(df_avg)

    st.download_button(
        "Download Comparative Report",
        df_avg.to_csv(index=False).encode(),
        "Comparative_Report.csv",
        "text/csv"
    )

# -------------------- TEMPLATE DOWNLOAD --------------------
st.subheader("Download Excel Template (Enter Marks Only)")

template_df = pd.DataFrame({
    'Name': [''],
    'Subject1': [''],
    'Subject2': [''],
    'Subject3': [''],
    'Subject4': [''],
    'Subject5': ['']
})

output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet('Instructions')
    worksheet.write('A1', 'Instructions for Teachers')
    worksheet.write('A3', '1. Do not change header names.')
    worksheet.write('A4', '2. Enter marks between 0 and 100 only.')
    worksheet.write('A5', '3. Do not add/delete columns.')

    template_df.to_excel(writer, sheet_name='Marks Entry', index=False)

st.download_button(
    "Download Excel Template",
    output.getvalue(),
    "API_5_Subjects_Template.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -------------------- APP UI --------------------
st.title("API Calculator for Teachers")
option = st.radio("Choose Analysis Type", (
    "Simple API (5 Subjects)",
    "Comparative Analysis",
    "Overall Class API"
))

if option == "Simple API (5 Subjects)":
    uploaded_file = st.file_uploader("Upload Filled Excel Template", type=["xlsx"])
    if uploaded_file:
        calculate_simple_api(uploaded_file)

elif option == "Comparative Analysis":
    files = st.file_uploader("Upload Multiple Assessment Files", type=["xlsx"], accept_multiple_files=True)
    if files:
        compare_assessments(files)

elif option == "Overall Class API":
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file:
        calculate_overall_api(uploaded_file)