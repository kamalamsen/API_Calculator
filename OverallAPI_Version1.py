import pandas as pd import streamlit as st from io import BytesIO

-------------------- COMMON UTILITIES --------------------

def normalize_headers(df): df.columns = df.columns.str.strip().str.lower() return df

-------------------- API LOGIC --------------------

def calculate_api_from_percentage(percentages): categories = [ (95, 100, 10), (90, 94.99, 8), (80, 89.99, 6), (70, 79.99, 4), (60, 69.99, 2), (50, 59.99, 0), (33, 49.99, -1), (0, 32.99, -3) ] total_weighted_score = 0 for pct in percentages: for low, high, weight in categories: if low <= pct <= high: total_weighted_score += weight break return (total_weighted_score / len(percentages)) * 100

-------------------- DIVISION --------------------

def division_bucket(pct): if pct >= 95: return '>95' elif pct >= 90: return '90-94.99' elif pct >= 80: return '80-89.99' elif pct >= 70: return '70-79.99' elif pct >= 60: return '60-69.99' elif pct >= 50: return '50-59.99' elif pct >= 33: return '33-49.99' else: return '<33'

DIVISION_ORDER = ['>95', '90-94.99', '80-89.99', '70-79.99', '60-69.99', '50-59.99', '33-49.99', '<33']

-------------------- SINGLE SUBJECT API (VIEW ONLY) --------------------

def calculate_single_subject_api(file): df = normalize_headers(pd.read_excel(file))

if not {'name', 'marks'}.issubset(df.columns):
    st.error('Excel must contain columns: Name, Marks')
    return

if df['marks'].max() > 100 or df['marks'].min() < 0:
    st.error('Marks must be between 0 and 100')
    return

df['percentage'] = df['marks']
df['division'] = df['percentage'].apply(division_bucket)

api_score = calculate_api_from_percentage(df['percentage'])
total_students = len(df)

st.markdown(f"## 📊 Single Subject API: **{api_score:.2f}**")
st.markdown(f"### 👥 **Total Students: {total_students}**")

div_df = df['division'].value_counts().reindex(DIVISION_ORDER, fill_value=0).reset_index()
div_df.columns = ['Division', 'Count']

st.subheader('Division-wise Distribution')
st.dataframe(div_df)

-------------------- FIVE SUBJECT API (CLASS VIEW + DOWNLOAD) --------------------

def calculate_five_subject_api(file): df = normalize_headers(pd.read_excel(file)) subject_cols = ['subject1', 'subject2', 'subject3', 'subject4', 'subject5']

if not all(col in df.columns for col in ['name'] + subject_cols):
    st.error('Excel must contain Name and Subject1 to Subject5')
    return

if df[subject_cols].max().max() > 100 or df[subject_cols].min().min() < 0:
    st.error('Marks must be between 0 and 100')
    return

df['total'] = df[subject_cols].sum(axis=1)
df['percentage'] = (df['total'] / 500) * 100
df['division'] = df['percentage'].apply(division_bucket)

api_score = calculate_api_from_percentage(df['percentage'])
total_students = len(df)

st.markdown(f"## 📊 Overall Class API: **{api_score:.2f}**")
st.markdown(f"### 👥 **Total Students: {total_students}**")

div_df = df['division'].value_counts().reindex(DIVISION_ORDER, fill_value=0).reset_index()
div_df.columns = ['Division', 'Count']

st.subheader('Division-wise Distribution')
st.dataframe(div_df)

# ---------------- DOWNLOAD (CLASS ONLY) ----------------
# Categories ONLY for Excel
def performance_tag(pct):
    if pct >= 95: return 'High Achiever'
    elif pct >= 75: return 'Average'
    elif pct >= 50: return 'Needs Improvement'
    elif pct >= 33: return 'Remedial'
    else: return 'Critical'

df['performance category'] = df['percentage'].apply(performance_tag)

output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Student Analysis', index=False)
    div_df.to_excel(writer, sheet_name='Division Summary', index=False)
    pd.DataFrame({
        'API Score': [api_score],
        'Total Students': [total_students]
    }).to_excel(writer, sheet_name='Summary', index=False)

st.download_button(
    'Download Class-wise Result Excel',
    output.getvalue(),
    'Class_API_Result.xlsx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

-------------------- TEMPLATES --------------------

st.subheader('Download Excel Templates')

single_template = pd.DataFrame({'Name': [''], 'Marks': ['']}) buf1 = BytesIO() with pd.ExcelWriter(buf1, engine='xlsxwriter') as writer: single_template.to_excel(writer, index=False)

st.download_button('Download Single Subject Template', buf1.getvalue(), 'Single_Subject_Template.xlsx')

five_template = pd.DataFrame({ 'Name': [''], 'Subject1': [''], 'Subject2': [''], 'Subject3': [''], 'Subject4': [''], 'Subject5': [''] }) buf2 = BytesIO() with pd.ExcelWriter(buf2, engine='xlsxwriter') as writer: five_template.to_excel(writer, index=False)

st.download_button('Download Five Subject Template', buf2.getvalue(), 'Five_Subject_Template.xlsx')

-------------------- UI --------------------

st.title('API Calculator for Teachers')

option = st.radio('Choose Calculation Type', ('Single Subject API', 'Overall Class API (5 Subjects)'))

if option == 'Single Subject API': uploaded_file = st.file_uploader('Upload Single Subject Excel', type=['xlsx']) if uploaded_file: calculate_single_subject_api(uploaded_file)

elif option == 'Overall Class API (5 Subjects)': uploaded_file = st.file_uploader('Upload Five Subject Excel', type=['xlsx']) if uploaded_file: calculate_five_subject_api(uploaded_file)
