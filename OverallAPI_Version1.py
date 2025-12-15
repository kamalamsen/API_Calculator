import pandas as pd
import streamlit as st
from io import BytesIO

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Teacher's API Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# -------------------- HELPER FUNCTIONS --------------------
def division_bucket(pct):
    if pct >= 95:
        return '>95'
    elif pct >= 90:
        return '90-94.99'
    elif pct >= 80:
        return '80-89.99'
    elif pct >= 70:
        return '70-79.99'
    elif pct >= 60:
        return '60-69.99'
    elif pct >= 50:
        return '50-59.99'
    elif pct >= 33:
        return '33-49.99'
    else:
        return '<33'

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

def get_category_color(category):
    colors = {
        'High Achiever': '🟢',
        'Average': '🟡',
        'Needs Improvement': '🟠',
        'Remedial': '🔴',
        'Critical': '⚫'
    }
    return colors.get(category, '')

def remedial_suggestion(cat):
    if cat == 'High Achiever':
        return 'Provide enrichment tasks and higher-order questions'
    elif cat == 'Average':
        return 'Regular practice with exam-oriented questions'
    elif cat == 'Needs Improvement':
        return 'Focused revision and topic-wise worksheets'
    elif cat == 'Remedial':
        return 'Small group remedial sessions and basics reinforcement'
    else:
        return 'Immediate intervention and personalised mentoring'

def teacher_remark(cat):
    if cat == 'High Achiever':
        return 'Excellent performance. Keep up the consistent effort.'
    elif cat == 'Average':
        return 'Good effort. With focused practice, further improvement is possible.'
    elif cat == 'Needs Improvement':
        return 'Needs more practice and regular revision to strengthen concepts.'
    elif cat == 'Remedial':
        return 'Requires remedial support and close academic monitoring.'
    else:
        return 'Immediate attention required. Individual guidance and parental support recommended.'

def weakness_remark(pct):
    if pct >= 75:
        return 'Concepts are clear. Continue with advanced practice.'
    elif pct >= 50:
        return 'Some topics need reinforcement through practice.'
    elif pct >= 33:
        return 'Basic concepts need strengthening.'
    else:
        return 'Major conceptual gaps observed.'

def board_remark(pct):
    if pct >= 90:
        return 'Well prepared for board-level questions.'
    elif pct >= 75:
        return 'On track for boards with regular revision.'
    elif pct >= 50:
        return 'Needs structured board-oriented practice.'
    else:
        return 'Requires intensive board exam preparation support.'

# -------------------- SINGLE SUBJECT API --------------------
def calculate_single_subject_api(file):
    try:
        df = normalize_headers(pd.read_excel(file))
        
        # Check required columns with better error message
        required_cols = {'name', 'marks'}
        available_cols = set(df.columns)
        missing_cols = required_cols - available_cols
        
        if missing_cols:
            st.error(f"""
            **❌ Missing Columns Detected**
            
            Your file is missing these required columns: **{', '.join(missing_cols)}**
            
            **Please ensure your file has exactly these columns:**
            - **Name** (Student names)
            - **Marks** (Scores out of 100)
            
            **Tip:** Use the template provided to avoid formatting issues.
            """)
            return
        
        # Validate marks range
        if df['marks'].max() > 100 or df['marks'].min() < 0:
            st.error("""
            **⚠️ Invalid Marks Range**
            
            All marks must be between **0 and 100**.
            
            Please check your data and upload again.
            """)
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Processing data...")
        progress_bar.progress(20)
        
        df['percentage'] = df['marks']
        df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)
        
        progress_bar.progress(40)
        status_text.text("Categorizing students...")
        
        df['division'] = df['percentage'].apply(division_bucket)
        df['performance category'] = df['percentage'].apply(performance_tag)
        df['suggested action'] = df['performance category'].apply(remedial_suggestion)
        df['teacher remark'] = df['performance category'].apply(teacher_remark)
        df['subject-wise remark'] = df['percentage'].apply(weakness_remark)
        df['board exam remark'] = df['percentage'].apply(board_remark)
        
        progress_bar.progress(60)
        status_text.text("Calculating API score...")
        
        api_score = calculate_api_from_percentage(df['percentage'])
        
        progress_bar.progress(80)
        status_text.text("Preparing reports...")
        
        # Clear progress indicators
        progress_bar.progress(100)
        status_text.text("")
        
        # Display Results
        st.success("✅ Analysis Complete!")
        
        # API Score in a prominent box
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h3 style='margin: 0; color: #1f77b4;'>🏆 Class API Score</h3>
                <h1 style='margin: 10px 0; color: #ff4b4b; font-size: 48px;'>{api_score:.2f}</h1>
                <p style='margin: 0; color: #666;'>Based on {len(df)} students</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary Statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", len(df))
        with col2:
            st.metric("Highest Score", f"{df['percentage'].max():.1f}%")
        with col3:
            st.metric("Average Score", f"{df['percentage'].mean():.1f}%")
        with col4:
            st.metric("Lowest Score", f"{df['percentage'].min():.1f}%")
        
        # Editable Remarks Section
        st.subheader("✏️ Edit Teacher Remarks")
        with st.expander("Click to edit remarks for individual students", expanded=False):
            edited = st.data_editor(
                df[['name', 'teacher remark']],
                num_rows='dynamic',
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("Student Name", width="medium"),
                    "teacher remark": st.column_config.TextColumn("Teacher Remark", width="large")
                }
            )
            df.update(edited)
        
        # Distribution Tables
        st.subheader("📈 Performance Distribution")
        
        tab1, tab2, tab3 = st.tabs(["By Division", "By Category", "Student Groups"])
        
        with tab1:
            div_df = df['division'].value_counts().reset_index()
            div_df.columns = ['Division', 'Count']
            div_df = div_df.sort_values('Division')
            st.dataframe(div_df, use_container_width=True)
            
            # Visualization
            st.bar_chart(div_df.set_index('Division'))
        
        with tab2:
            cat_df = df['performance category'].value_counts().reset_index()
            cat_df.columns = ['Category', 'Count']
            # Add emoji for better visualization
            cat_df['Display'] = cat_df['Category'].apply(lambda x: f"{get_category_color(x)} {x}")
            st.dataframe(cat_df[['Display', 'Count']], use_container_width=True)
        
        with tab3:
            for cat in df['performance category'].unique():
                cat_count = len(df[df['performance category'] == cat])
                with st.expander(f"{get_category_color(cat)} {cat} ({cat_count} students)", expanded=False):
                    st.dataframe(
                        df[df['performance category'] == cat][['name', 'percentage', 'rank', 'teacher remark']]
                        .sort_values('rank'),
                        use_container_width=True
                    )
        
        # Download Section
        st.subheader("💾 Download Full Report")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Student Analysis', index=False)
            div_df.to_excel(writer, sheet_name='Division Summary', index=False)
            cat_df[['Category', 'Count']].to_excel(writer, sheet_name='Category Summary', index=False)
            pd.DataFrame({
                'Metric': ['API Score', 'Total Students', 'Highest Score', 'Average Score', 'Lowest Score'],
                'Value': [api_score, len(df), df['percentage'].max(), df['percentage'].mean(), df['percentage'].min()]
            }).to_excel(writer, sheet_name='Summary', index=False)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name='API_Single_Subject_Report.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"""
        **❌ Error Processing File**
        
        There was an issue with your file:
        ```
        {str(e)}
        ```
        
        **Please check:**
        1. File is in .xlsx format
        2. No empty rows before the data
        3. No merged cells
        4. Use the template for correct format
        """)

# -------------------- FIVE SUBJECT API --------------------
def calculate_five_subject_api(file):
    try:
        df = normalize_headers(pd.read_excel(file))
        subject_cols = ['subject1', 'subject2', 'subject3', 'subject4', 'subject5']
        
        # Check required columns
        required_cols = set(['name'] + subject_cols)
        available_cols = set(df.columns)
        missing_cols = required_cols - available_cols
        
        if missing_cols:
            st.error(f"""
            **❌ Missing Columns Detected**
            
            Your file is missing these required columns: **{', '.join(missing_cols)}**
            
            **Please ensure your file has these columns:**
            - **Name** (Student names)
            - **Subject1** to **Subject5** (Marks out of 100 for each subject)
            
            **Tip:** Use the Five Subjects template for correct format.
            """)
            return
        
        # Validate marks range
        if df[subject_cols].max().max() > 100 or df[subject_cols].min().min() < 0:
            st.error("""
            **⚠️ Invalid Marks Range**
            
            All subject marks must be between **0 and 100**.
            
            Please check your data and upload again.
            """)
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Processing data...")
        progress_bar.progress(20)
        
        df['total'] = df[subject_cols].sum(axis=1)
        df['percentage'] = (df['total'] / 500) * 100
        
        progress_bar.progress(40)
        status_text.text("Calculating ranks and categories...")
        
        df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)
        df['division'] = df['percentage'].apply(division_bucket)
        df['performance category'] = df['percentage'].apply(performance_tag)
        df['suggested action'] = df['performance category'].apply(remedial_suggestion)
        df['teacher remark'] = df['performance category'].apply(teacher_remark)
        df['subject-wise remark'] = df['percentage'].apply(weakness_remark)
        df['board exam remark'] = df['percentage'].apply(board_remark)
        
        progress_bar.progress(60)
        status_text.text("Calculating API score...")
        
        api_score = calculate_api_from_percentage(df['percentage'])
        
        progress_bar.progress(80)
        status_text.text("Preparing reports...")
        
        # Clear progress indicators
        progress_bar.progress(100)
        status_text.text("")
        
        # Display Results
        st.success("✅ Analysis Complete!")
        
        # API Score in a prominent box
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h3 style='margin: 0; color: #1f77b4;'>🏆 Class API Score</h3>
                <h1 style='margin: 10px 0; color: #ff4b4b; font-size: 48px;'>{api_score:.2f}</h1>
                <p style='margin: 0; color: #666;'>Based on {len(df)} students across 5 subjects</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary Statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", len(df))
        with col2:
            st.metric("Highest Percentage", f"{df['percentage'].max():.1f}%")
        with col3:
            st.metric("Average Percentage", f"{df['percentage'].mean():.1f}%")
        with col4:
            st.metric("Lowest Percentage", f"{df['percentage'].min():.1f}%")
        
        # Subject-wise Averages
        st.subheader("📚 Subject-wise Performance")
        subject_avgs = df[subject_cols].mean().round(2)
        subject_df = pd.DataFrame({
            'Subject': [f'Subject {i+1}' for i in range(5)],
            'Average Score': subject_avgs.values
        })
        st.dataframe(subject_df, use_container_width=True)
        
        # Editable Remarks Section
        st.subheader("✏️ Edit Teacher Remarks")
        with st.expander("Click to edit remarks for individual students", expanded=False):
            edited = st.data_editor(
                df[['name', 'teacher remark']],
                num_rows='dynamic',
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("Student Name", width="medium"),
                    "teacher remark": st.column_config.TextColumn("Teacher Remark", width="large")
                }
            )
            df.update(edited)
        
        # Distribution Tables
        st.subheader("📈 Performance Distribution")
        
        tab1, tab2, tab3 = st.tabs(["By Division", "By Category", "Student Groups"])
        
        with tab1:
            div_df = df['division'].value_counts().reset_index()
            div_df.columns = ['Division', 'Count']
            div_df = div_df.sort_values('Division')
            st.dataframe(div_df, use_container_width=True)
            
            # Visualization
            st.bar_chart(div_df.set_index('Division'))
        
        with tab2:
            cat_df = df['performance category'].value_counts().reset_index()
            cat_df.columns = ['Category', 'Count']
            # Add emoji for better visualization
            cat_df['Display'] = cat_df['Category'].apply(lambda x: f"{get_category_color(x)} {x}")
            st.dataframe(cat_df[['Display', 'Count']], use_container_width=True)
        
        with tab3:
            for cat in df['performance category'].unique():
                cat_count = len(df[df['performance category'] == cat])
                with st.expander(f"{get_category_color(cat)} {cat} ({cat_count} students)", expanded=False):
                    st.dataframe(
                        df[df['performance category'] == cat][['name', 'percentage', 'total', 'rank', 'teacher remark']]
                        .sort_values('rank'),
                        use_container_width=True
                    )
        
        # Top Performers
        st.subheader("🏅 Top 10 Performers")
        top_10 = df.nlargest(10, 'percentage')[['name', 'total', 'percentage', 'rank']]
        st.dataframe(top_10, use_container_width=True)
        
        # Download Section
        st.subheader("💾 Download Full Report")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Student Analysis', index=False)
            div_df.to_excel(writer, sheet_name='Division Summary', index=False)
            cat_df[['Category', 'Count']].to_excel(writer, sheet_name='Category Summary', index=False)
            subject_df.to_excel(writer, sheet_name='Subject Averages', index=False)
            pd.DataFrame({
                'Metric': ['API Score', 'Total Students', 'Highest %', 'Average %', 'Lowest %'],
                'Value': [api_score, len(df), df['percentage'].max(), df['percentage'].mean(), df['percentage'].min()]
            }).to_excel(writer, sheet_name='Summary', index=False)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name='API_Five_Subjects_Report.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"""
        **❌ Error Processing File**
        
        There was an issue with your file:
        ```
        {str(e)}
        ```
        
        **Please check:**
        1. File is in .xlsx format
        2. All 5 subject columns are present
        3. No empty rows before the data
        4. No merged cells
        5. Use the template for correct format
        """)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center;'>
        <h1>📊</h1>
        <h2>Teacher's API Calculator</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("📋 Choose Analysis Type")
    option = st.radio(
        "",
        ('Single Subject API', 'Five Subject API'),
        help="Select based on your data format"
    )
    
    st.markdown("---")
    
    st.subheader("ℹ️ How to Use")
    with st.expander("Step-by-Step Guide", expanded=True):
        st.markdown(f"""
        **For {option}:**
        
        1. **📥 Download** the {option.split()[0].lower()} template
        2. **✏️ Fill** with student marks (0-100)
        3. **📤 Upload** your filled file
        4. **📊 View** results and analysis
        5. **💾 Download** detailed report
        
        **Note:** 
        - Use the template for correct format
        - Save your file as .xlsx
        - Don't rename or delete columns
        """)
    
    st.markdown("---")
    
    st.subheader("📞 Need Help?")
    st.markdown("""
    **Common Issues:**
    - File not uploading? → Check .xlsx format
    - Error message? → Use the template
    - Wrong results? → Verify marks are 0-100
    
    **Tips:**
    - Download template first
    - Don't edit column names
    - Save before uploading
    """)
    
    st.markdown("---")
    st.caption("Made for Teachers • Easy Grade Analysis")

# -------------------- MAIN CONTENT --------------------
st.title(f"🎯 {option}")

# Templates Section
st.header("1. 📥 Get Your Template")

if option == 'Single Subject API':
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Template Format")
        example_df = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith', 'Robert Johnson', 'Emily Davis'],
            'Marks': [85, 92, 78, 65]
        })
        st.dataframe(example_df, use_container_width=True)
        st.caption("**Note:** Marks should be out of 100")
    
    with col2:
        st.subheader("⬇️ Download Template")
        single_template = pd.DataFrame({'Name': [''], 'Marks': ['']})
        buf1 = BytesIO()
        with pd.ExcelWriter(buf1, engine='xlsxwriter') as writer:
            single_template.to_excel(writer, index=False, sheet_name='Template')
        
        st.download_button(
            label="📥 Download Single Subject Template",
            data=buf1.getvalue(),
            file_name='Single_Subject_Template.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True
        )
        
        st.info("💡 **Tip:** Fill this template with your student data, then upload below.")
        
else:  # Five Subject API
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Template Format")
        example_df = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Subject1': [85, 92],
            'Subject2': [78, 88],
            'Subject3': [92, 85],
            'Subject4': [67, 90],
            'Subject5': [89, 94]
        })
        st.dataframe(example_df, use_container_width=True)
        st.caption("**Note:** All marks should be out of 100 (5 subjects)")
    
    with col2:
        st.subheader("⬇️ Download Template")
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
            five_template.to_excel(writer, index=False, sheet_name='Template')
        
        st.download_button(
            label="📥 Download Five Subjects Template",
            data=buf2.getvalue(),
            file_name='Five_Subjects_Template.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True
        )
        
        st.info("💡 **Tip:** Total and percentage will be automatically calculated.")

st.header("2. 📤 Upload Your Filled File")

uploaded_file = st.file_uploader(
    f"Choose your {option} Excel file",
    type=['xlsx'],
    help="Upload the filled template file (.xlsx format only)"
)

if uploaded_file:
    st.success(f"✅ File uploaded successfully: **{uploaded_file.name}**")
    
    # Show file info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.1f} KB"
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📄 **File:** {file_details['Filename']}")
    with col2:
        st.info(f"📏 **Size:** {file_details['File size']}")
    
    st.header("3. 📊 View Results")
    
    # Process the file
    if option == 'Single Subject API':
        calculate_single_subject_api(uploaded_file)
    else:
        calculate_five_subject_api(uploaded_file)
else:
    st.info("👆 **Please upload your Excel file to see the analysis results.**")
    
    # Show what happens next
    st.markdown("---")
    st.subheader("🎬 What Happens Next?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background-color: #e6f3ff; border-radius: 10px;'>
            <h3>1️⃣</h3>
            <p><b>Upload File</b></p>
            <small>Your data is processed securely</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background-color: #e6f3ff; border-radius: 10px;'>
            <h3>2️⃣</h3>
            <p><b>Instant Analysis</b></p>
            <small>API score, ranks, categories</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 15px; background-color: #e6f3ff; border-radius: 10px;'>
            <h3>3️⃣</h3>
            <p><b>Download Report</b></p>
            <small>Complete Excel with all details</small>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📚 <b>Teacher's API Calculator</b> • Simplify Your Grade Analysis</p>
    <small>All processing happens in your browser. Your data is never stored on our servers.</small>
</div>
""", unsafe_allow_html=True)
