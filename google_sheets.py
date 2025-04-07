import streamlit as st
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from sentiment import analyze_dataframe_sentiment

def analyze_google_sheets():
    """Handle Google Sheets analysis workflow."""
    st.subheader("Analysis Via Google Sheets")
    
    sid = st.text_input("Enter your Google Sheet ID")
    range_input = st.text_input("Enter the Range between first column and last column.")
    column_name = st.text_input("Enter column name that is to be analyzed.")
    
    btn = st.button("Analyze")
    
    if btn:
        if not all([sid, range_input, column_name]):
            st.error("Please fill in all fields.")
            return
        
        try:
            # Initialize Google Sheets API credentials
            if 'cred' not in st.session_state:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "key.json", 
                    ["https://www.googleapis.com/auth/spreadsheets"]
                )
                st.session_state.cred = flow.run_local_server(port=0)
            
            # Build the service
            service = build('sheets', 'v4', credentials=st.session_state.cred).spreadsheets().values()
            response = service.get(spreadsheetId=sid, range=range_input).execute()
            data = response['values']
            
            # Convert the retrieved data into a pandas DataFrame
            df = pd.DataFrame(data=data[1:], columns=data[0])
            
            # Perform sentiment analysis
            result_df = analyze_dataframe_sentiment(df, column_name)
            
            # Save results to CSV
            os.makedirs('data', exist_ok=True)
            results_path = "data/results.csv"
            result_df.to_csv(results_path, index=False)
            
            # Display the results dataframe
            st.subheader("Sentiment Analysis Results")
            st.dataframe(result_df)
            
            # Add a download button for the results
            st.download_button(
                label="Download Results",
                data=result_df.to_csv(index=False),
                file_name="google_sheets_analysis_results.csv",
                mime="text/csv"
            )
            
            st.success(f"Results saved as {results_path}")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")