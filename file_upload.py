import streamlit as st
import pandas as pd
import os
from sentiment import analyze_dataframe_sentiment

def analyze_file_upload():
    """Handle file upload analysis workflow."""
    st.subheader("Upload a CSV or Excel File for Sentiment Analysis")
    
    uploaded_file = st.file_uploader("Choose a file (CSV or Excel)", type=['csv', 'xlsx'])
    column_name = st.text_input("Enter the column name to be analyzed for sentiment.")
    
    btn = st.button("Start Analysis")
    
    if btn:
        if not uploaded_file:
            st.error("Please upload a file before starting the analysis.")
            return
            
        try:
            # Read the uploaded file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            
            if column_name not in df.columns:
                st.error(f"Invalid column name '{column_name}'. Please enter a valid column name.")
                st.write("Available columns:", ", ".join(df.columns))
                return
            
            # Perform sentiment analysis
            result_df = analyze_dataframe_sentiment(df, column_name)
            
            # Save results
            os.makedirs('data', exist_ok=True)
            results_path = "data/results.csv"
            result_df.to_csv(results_path, index=False)
            
            # Display success message and preview results
            st.success("Sentiment analysis completed!")
            st.dataframe(result_df.head(100))
            
            # Provide download button
            st.download_button(
                label="Download Results",
                data=result_df.to_csv(index=False),
                file_name="file_upload_analysis_results.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")