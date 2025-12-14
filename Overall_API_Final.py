import pandas as pd
import streamlit as st
from io import BytesIO

# -------------------- COMMON UTILITIES --------------------
def normalize_headers(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

# -------------------- API LOGIC (COMMON) --------------------
def calculate_api_from_percentage(percentages):
    categories = [
        (95, 100, 10),
        (90, 94.99, 8),
        (80, 89.99, 6),
        (70, 79.99, 4),
        (60, 69.99, 2),
        (50, 59.99, 0),
        (33, 49.99, -1),
        (0, 32.99, -3),
    ]
    total_weighted_score = 0
    for pct in percentages:
        for low, high, weight in categories:
            if low <= pct <= high:
                total_weighted_score += weight
                break
    return (total_weighted_score / len(percentages)) * 100

# -------------------- SINGLE SUBJECT API --------------------
def calculate_single_subject_api(file):
    df = normalize_headers(pd.read_excel(file))

    if not {'name', 'marks'}.issubset(df.columns):
        st.error("Excel must contain columns: Name, Marks")
        return

    if df['marks'].max() > 100 or df['marks'].min() < 0:
        st.error("Marks must be between 0 and 100")
        return

    df['percentage'] = df['marks']
    # Ranking only for single subject
    df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)

    api_score = calculate_api_from_percentage(df['percentage'])

    st.subheader("Single Subject API Result")
    st.dataframe(df)
    st.write(f"Class API Score: {api_score:.2f}")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Processed Data', index=False)
        pd.DataFrame({'API Score': [api_score]}).to_excel(writer, sheet_name='Summary', index=False)

    st.download_button(
        "Download Final Excel",
        output.getvalue(),
        "API_Single_Subject.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------- FIVE SUBJECT API --------------------
def calculate_five_subject_api(file):
    df = normalize_headers(pd.read_excel(file))
    subject_cols = ['subject1', 'subject2', 'subject3', 'subject4', 'subject5']

    if not all(col in df.columns for col in ['name'] + subject_cols):
        st.error("Excel must contain Name and Subject1 to Subject5")
        return

    if df[subject_cols].max().max() > 100 or df[subject_cols].min().min() < 0:
        st.error("Marks must be between 0 and 100")
        return

    df['total'] = df[subject_cols].sum(axis=1)
    df['percentage'] = (df['total'] / 500) * 100

    # Performance category for five-subject API
    def performance_tag(pct):
        if pct >= 95:
            return 'High Achiever'
        elif pct >= 75:
            return 'Average'
        elif pct >= 50:
            return 'Needs Improvement'
        elif pct >= 33:
            return 'Remedial'
        else:
            return 'Critical'

    df['performance category'] = df['percentage'].apply(performance_tag)

    # Ranking for five-subject API
    df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)

    api_score = calculate_api_from_percentage(df['percentage'])

    st.subheader("Five Subject API Result")
    st.dataframe(df)
    st.write(f"Class API Score: {api_score:.2f}")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Processed Data', index=False)
        pd.DataFrame({'API Score': [api_score]}).to_excel(writer, sheet_name='Summary', index=False)

    st.download_button(
        "Download Final Excel",
        output.getvalue(),
        "API_Five_Subjects.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------- TEMPLATE DOWNLOADS --------------------
st.subheader("Download Excel Templates")

# Single subject template
single_template = pd.DataFrame({'Name': [''], 'Marks': ['']})
buf1 = BytesIO()
with pd.ExcelWriter(buf1, engine='xlsxwriter') as writer:
    single_template.to_excel(writer, index=False)

st.download_button(
    "Download Single Subject Template",
    buf1.getvalue(),
    "Single_Subject_Template.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Five subject template
five_template = pd.DataFrame({
    'Name': [''],
    'Subject1': [''],
    'Subject2': [''],
    'Subject3': [''],
    'Subject4': [''],
    'Subject5': ['']
})
buf2 = BytesIO()
with pd.ExcelWriter(buf2, engine='xlsxwriter') as writer:
    five_template.to_excel(writer, index=False)

st.download_button(
    "Download Five Subject Template",
    buf2.getvalue(),
    "Five_Subject_Template.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -------------------- APP UI --------------------
st.title("API Calculator for Teachers")

st.markdown("""
### How to use – Single Subject API
1. Download **Single Subject Template**
2. Enter student names and marks (out of 100)
3. Upload the filled file
4. Download the processed Excel with API

### How to use – Five Subject API
1. Download **Five Subject Template**
2. Enter marks for all 5 subjects (each out of 100)
3. Upload the filled file
4. Download the processed Excel with Total, Percentage and API
""")

option = st.radio("Choose Calculation Type", (
    "Single Subject API",
    "Five Subject API"
))

if option == "Single Subject API":
    uploaded_file = st.file_uploader("Upload Single Subject Excel", type=["xlsx"])
    if uploaded_file:
        calculate_single_subject_api(uploaded_file)

elif option == "Five Subject API":
    uploaded_file = st.file_uploader("Upload Five Subject Excel", type=["xlsx"])
    if uploaded_file:
        calculate_five_subject_api(uploaded_file)
