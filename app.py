import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
import numpy as np

def ai_based_student_categorization(file):
    df = pd.read_excel(file)

    if not {'Name', 'Marks'}.issubset(df.columns):
        st.error("Excel file must contain 'Name' and 'Marks' columns.")
        return

    marks = df[['Marks']].values  # Extract marks as input for clustering

    # Optimal cluster count (We assume 3: High Achievers, Average, Needs Improvement)
    num_clusters = 3  

    # Apply K-Means Clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(marks)  # <- Fixed closing parenthesis issue

    # Assign meaningful cluster labels dynamically
    cluster_mapping = {}
    sorted_indices = np.argsort(kmeans.cluster_centers_.flatten())

    cluster_mapping[sorted_indices[0]] = "Needs Improvement"
    cluster_mapping[sorted_indices[1]] = "Average"
    cluster_mapping[sorted_indices[2]] = "High Achiever"

    df['Category'] = df['Cluster'].map(cluster_mapping)

    # Show results in Streamlit
    st.write("### AI-Based Student Categorization Results")
    st.dataframe(df[['Name', 'Marks', 'Category']])

    # Count students in each category
    category_counts = df['Category'].value_counts()
    st.bar_chart(category_counts)

    # Provide Download Option
    csv = df[['Name', 'Marks', 'Category']].to_csv(index=False).encode('utf-8')
    st.download_button("Download Categorized Student Report", csv, "student_categories.csv", "text/csv")

# Streamlit UI
st.title("AI-Based Student Categorization")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    ai_based_student_categorization(uploaded_file)
