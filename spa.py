import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

BASE_FOLDER = "class_data"  # Main folder to store class-wise data

# Function to create a folder for a class
def create_class_folder(class_name):
    """Create a folder for the class if it doesn't exist"""
    class_folder = os.path.join(BASE_FOLDER, class_name)
    if not os.path.exists(class_folder):
        os.makedirs(class_folder)
    return class_folder

# Function to save test results per class
def save_class_test_results(class_name, df):
    """Save test results in a CSV file for the given class"""
    class_folder = create_class_folder(class_name)
    file_path = os.path.join(class_folder, "student_performance.csv")
    
    if os.path.exists(file_path):
        old_data = pd.read_csv(file_path)
        df = pd.concat([old_data, df])  # Append new test results
    df.to_csv(file_path, index=False)

# Function to load past student performance for a class
def load_past_performance(class_name):
    """Load stored test results for a class"""
    class_folder = os.path.join(BASE_FOLDER, class_name)
    file_path = os.path.join(class_folder, "student_performance.csv")
    
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path)

# Function to analyze student performance using K-Means Clustering
def analyze_class_performance(class_name):
    """Analyze student performance and categorize them"""
    df = load_past_performance(class_name)
    
    if df is None:
        st.error(f"No data found for Class {class_name}. Please upload test data first.")
        return
    
    # K-Means Clustering for performance categorization
    num_clusters = 3  # High Achiever, Average, Needs Improvement
    marks = df[['Marks']].values
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(marks)

    # Assign meaningful labels to clusters
    sorted_indices = np.argsort(kmeans.cluster_centers_.flatten())
    cluster_mapping = {
        sorted_indices[0]: "Needs Improvement",
        sorted_indices[1]: "Average",
        sorted_indices[2]: "High Achiever"
    }
    df['Category'] = df['Cluster'].map(cluster_mapping)

    # Save updated data with categories
    save_class_test_results(class_name, df)

    # Display results
    st.write(f"### Performance Analysis for Class {class_name}")
    st.dataframe(df[['Name', 'Marks', 'Category']])

    # Show student distribution in different categories
    category_counts = df['Category'].value_counts()
    st.bar_chart(category_counts)

# Function to compare performance between multiple classes
def compare_classes(class_list):
    """Compare average performance of multiple classes"""
    avg_marks = {}
    
    for class_name in class_list:
        df = load_past_performance(class_name)
        if df is not None:
            avg_marks[class_name] = df["Marks"].mean()

    if avg_marks:
        st.write("### Class Performance Comparison")
        st.bar_chart(avg_marks)
    else:
        st.error("No test data found for the selected classes.")

# Streamlit App UI
st.title("Multi-Class AI-Based Student Performance Analyzer")

# Select a class for analysis
class_name = st.text_input("Enter Class & Section (e.g., 10A, 9B)")

# Upload new test results
uploaded_file = st.file_uploader("Upload Excel file (with 'Name' and 'Marks' columns)", type=["xlsx"])
if uploaded_file and class_name:
    df = pd.read_excel(uploaded_file)
    if {'Name', 'Marks'}.issubset(df.columns):
        save_class_test_results(class_name, df)
        st.success(f"Test results saved for Class {class_name}")
    else:
        st.error("Excel file must contain 'Name' and 'Marks' columns.")

# Analyze performance for a specific class
if st.button("Analyze Class Performance") and class_name:
    analyze_class_performance(class_name)

# Compare multiple classes
class_list = st.text_area("Enter Class Names for Comparison (comma-separated, e.g., 10A, 9B)")
if st.button("Compare Classes") and class_list:
    compare_classes(class_list.split(","))
