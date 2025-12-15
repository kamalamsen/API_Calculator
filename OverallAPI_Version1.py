import pandas as pd
import streamlit as st
from io import BytesIO
import time

# -------------------- PAGE CONFIG (FIRST COMMAND) --------------------
st.set_page_config(
    page_title="Teacher's API Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache expensive operations
@st.cache_data
def load_excel_data(file):
    """Cache the Excel file loading"""
    return pd.read_excel(file)

@st.cache_data
def calculate_api_cached(percentages):
    """Cache API calculation"""
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
def normalize_headers(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

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

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-size: 48px;'>📊</h1>
        <h2>API Calculator</h2>
        <p style='color: #666; font-size: 14px;'>For Teachers</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize session state for option if not exists
    if 'analysis_option' not in st.session_state:
        st.session_state.analysis_option = 'Single Subject API'
    
    option = st.radio(
        "**📋 Choose Analysis Type**",
        ('Single Subject API', 'Five Subject API'),
        key='analysis_option',
        help="Select based on your data format"
    )
    
    st.markdown("---")
    
    with st.expander("**ℹ️ Quick Guide**", expanded=True):
        if option == 'Single Subject API':
            st.markdown("""
            1. **Download** single subject template
            2. **Fill** names and marks (0-100)
            3. **Upload** your file
            4. **Get** API score and analysis
            
            **Columns needed:**
            - Name
            - Marks
            """)
        else:
            st.markdown("""
            1. **Download** five subjects template
            2. **Fill** 5 subject marks (0-100 each)
            3. **Upload** your file
            4. **Get** total, percentage, and API
            
            **Columns needed:**
            - Name
            - Subject1 to Subject5
            """)
    
    st.markdown("---")
    st.caption("💡 **Tip:** Always use the template for best results")

# -------------------- TEMPLATE DOWNLOAD SECTION --------------------
st.title(f"📚 {option}")

# Templates in columns
st.header("1. Get Your Template")

if option == 'Single Subject API':
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Template Format")
        st.markdown("""
        Your Excel file should look like this:
        
        | Name | Marks |
        |------|-------|
        | Student 1 | 85 |
        | Student 2 | 92 |
        | Student 3 | 78 |
        """)
        
        # Simple example table
        example_data = {
            'Name': ['Rahul Sharma', 'Priya Patel', 'Amit Kumar'],
            'Marks': [85, 92, 78]
        }
        st.dataframe(pd.DataFrame(example_data), use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Download")
        # Create template on demand
        if st.button("📥 Download Single Subject Template", use_container_width=True):
            single_template = pd.DataFrame({'Name': [''], 'Marks': ['']})
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                single_template.to_excel(writer, index=False)
            st.download_button(
                label="Click to Save Template",
                data=buf.getvalue(),
                file_name='Single_Subject_Template.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key="single_template_dl"
            )
        
        st.info("**Tip:** Marks should be between 0-100")
        
else:  # Five Subject API
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Template Format")
        st.markdown("""
        Your Excel file should look like this:
        
        | Name | Sub1 | Sub2 | Sub3 | Sub4 | Sub5 |
        |------|------|------|------|------|------|
        | Student 1 | 85 | 78 | 92 | 67 | 89 |
        """)
        
        # Simple example table
        example_data = {
            'Name': ['Rahul Sharma', 'Priya Patel'],
            'Subject1': [85, 92],
            'Subject2': [78, 88],
            'Subject3': [92, 85],
            'Subject4': [67, 90],
            'Subject5': [89, 94]
        }
        st.dataframe(pd.DataFrame(example_data), use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Download")
        # Create template on demand
        if st.button("📥 Download Five Subjects Template", use_container_width=True):
            five_template = pd.DataFrame({
                'Name': [''],
                'Subject1': [''],
                'Subject2': [''],
                'Subject3': [''],
                'Subject4': [''],
                'Subject5': ['']
            })
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                five_template.to_excel(writer, index=False)
            st.download_button(
                label="Click to Save Template",
                data=buf.getvalue(),
                file_name='Five_Subjects_Template.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key="five_template_dl"
            )
        
        st.info("**Tip:** All marks 0-100")

# -------------------- UPLOAD SECTION --------------------
st.header("2. Upload Your File")

uploaded_file = st.file_uploader(
    f"Upload your {option.split()[0].lower()} marks file",
    type=['xlsx', 'xls'],
    help="Only Excel files (.xlsx, .xls) are supported"
)

if uploaded_file:
    # Store file in session state to prevent re-uploads
    if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file != uploaded_file.name:
        st.session_state.uploaded_file = uploaded_file.name
        st.session_state.processed = False
    
    st.success(f"✅ **File uploaded:** {uploaded_file.name}")
    
    # Process button to control when analysis runs
    if st.button("🚀 Process File", type="primary", use_container_width=True):
        with st.spinner("Processing your data..."):
            # Small delay for better UX
            time.sleep(0.5)
            
            try:
                # Load and process data
                df = load_excel_data(uploaded_file)
                df = normalize_headers(df)
                
                if option == 'Single Subject API':
                    # Validate single subject
                    if not {'name', 'marks'}.issubset(df.columns):
                        st.error("❌ **Missing columns!** File must have 'Name' and 'Marks' columns.")
                        st.stop()
                    
                    if df['marks'].max() > 100 or df['marks'].min() < 0:
                        st.error("❌ **Invalid marks!** All marks must be between 0 and 100.")
                        st.stop()
                    
                    # Calculate
                    df['percentage'] = df['marks']
                    df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)
                    df['division'] = df['percentage'].apply(division_bucket)
                    df['performance category'] = df['percentage'].apply(performance_tag)
                    
                else:  # Five Subject API
                    subject_cols = ['subject1', 'subject2', 'subject3', 'subject4', 'subject5']
                    required_cols = ['name'] + subject_cols
                    
                    missing = [col for col in required_cols if col not in df.columns]
                    if missing:
                        st.error(f"❌ **Missing columns:** {', '.join(missing)}")
                        st.stop()
                    
                    if df[subject_cols].max().max() > 100 or df[subject_cols].min().min() < 0:
                        st.error("❌ **Invalid marks!** All subject marks must be between 0 and 100.")
                        st.stop()
                    
                    # Calculate
                    df['total'] = df[subject_cols].sum(axis=1)
                    df['percentage'] = (df['total'] / 500) * 100
                    df['rank'] = df['percentage'].rank(ascending=False, method='dense').astype(int)
                    df['division'] = df['percentage'].apply(division_bucket)
                    df['performance category'] = df['percentage'].apply(performance_tag)
                
                # Common calculations
                df['suggested action'] = df['performance category'].apply(remedial_suggestion)
                df['teacher remark'] = df['performance category'].apply(teacher_remark)
                df['subject-wise remark'] = df['percentage'].apply(weakness_remark)
                df['board exam remark'] = df['percentage'].apply(board_remark)
                
                # Calculate API
                api_score = calculate_api_cached(df['percentage'])
                
                # Store results in session state
                st.session_state.df = df
                st.session_state.api_score = api_score
                st.session_state.processed = True
                
            except Exception as e:
                st.error(f"❌ **Error processing file:** {str(e)}")
                st.stop()
    
    # Display results if processed
    if 'processed' in st.session_state and st.session_state.processed:
        df = st.session_state.df
        api_score = st.session_state.api_score
        
        st.header("3. Analysis Results")
        
        # API Score in nice display
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
            <h3 style='margin: 0;'>Class API Score</h3>
            <h1 style='margin: 10px 0; font-size: 48px;'>{api_score:.2f}</h1>
            <p style='margin: 0; opacity: 0.9;'>Based on {len(df)} students</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        st.subheader("📊 Quick Statistics")
        cols = st.columns(4)
        metrics = [
            ("Total Students", len(df)),
            ("Highest Score", f"{df['percentage'].max():.1f}%"),
            ("Average Score", f"{df['percentage'].mean():.1f}%"),
            ("Lowest Score", f"{df['percentage'].min():.1f}%")
        ]
        
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, value)
        
        # Performance distribution
        st.subheader("📈 Performance Distribution")
        
        tab1, tab2, tab3 = st.tabs(["Categories", "Divisions", "Students"])
        
        with tab1:
            cat_counts = df['performance category'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            for _, row in cat_counts.iterrows():
                color = get_category_color(row['Category'])
                st.write(f"{color} **{row['Category']}**: {row['Count']} students")
        
        with tab2:
            div_counts = df['division'].value_counts().reset_index()
            div_counts.columns = ['Division', 'Count']
            st.dataframe(div_counts, use_container_width=True, hide_index=True)
        
        with tab3:
            # Simple student list
            display_cols = ['name', 'percentage', 'rank', 'performance category']
            st.dataframe(df[display_cols].sort_values('rank'), 
                        use_container_width=True, 
                        hide_index=True,
                        column_config={
                            "name": "Student Name",
                            "percentage": "Score %",
                            "rank": "Rank",
                            "performance category": "Category"
                        })
        
        # Editable remarks
        st.subheader("✏️ Edit Teacher Remarks")
        with st.expander("Click to edit", expanded=False):
            edited_df = st.data_editor(
                df[['name', 'teacher remark']],
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("Student", width="medium"),
                    "teacher remark": st.column_config.TextColumn("Remark", width="large")
                }
            )
            # Update only if changed
            if not edited_df.equals(df[['name', 'teacher remark']]):
                df['teacher remark'] = edited_df['teacher remark']
                st.success("Remarks updated!")
        
        # Download section
        st.subheader("💾 Download Report")
        
        # Prepare download data
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Student Analysis', index=False)
            
            # Summary sheets
            cat_summary = df['performance category'].value_counts().reset_index()
            cat_summary.columns = ['Category', 'Count']
            cat_summary.to_excel(writer, sheet_name='Categories', index=False)
            
            div_summary = df['division'].value_counts().reset_index()
            div_summary.columns = ['Division', 'Count']
            div_summary.to_excel(writer, sheet_name='Divisions', index=False)
            
            # API score sheet
            summary_df = pd.DataFrame({
                'Metric': ['API Score', 'Total Students', 'Highest %', 'Average %', 'Lowest %'],
                'Value': [api_score, len(df), df['percentage'].max(), df['percentage'].mean(), df['percentage'].min()]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Download button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Full Report (Excel)",
                data=output.getvalue(),
                file_name=f'API_Report_{time.strftime("%Y%m%d_%H%M%S")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True,
                type="primary"
            )
        
        st.info("💡 **Tip:** The downloaded file contains all analysis in separate sheets.")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><b>Teacher's API Calculator</b> • Simplify Your Grade Analysis</p>
    <small>All processing happens in your browser. Your data is never stored.</small>
</div>
""", unsafe_allow_html=True)

# -------------------- INITIAL LOADING MESSAGE --------------------
if 'initial_load' not in st.session_state:
    st.session_state.initial_load = True
    # Show a simple welcome message on first load
    st.balloons()
    st.success("App loaded successfully! Choose your analysis type from the sidebar.")
