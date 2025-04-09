import streamlit as st
import home, google_sheets, file_upload, results, llm_summarization
import report_generation, chart_export

st.set_page_config(page_title="Amazon Sentiment Analysis System")

st.title("Amazon Review Sentiment Analysis System")
choice = st.sidebar.selectbox("My Menu", (
    "Home", 
    "Analysis Via Google Sheets", 
    "Analysis Via File Upload", 
    "Results", 
    "AI Summarization",
    "Export Charts",
    "Generate Reports"
))

# Route to the appropriate page based on user selection
if choice == "Home":
    home.show_home()
elif choice == "Analysis Via Google Sheets":
    google_sheets.analyze_google_sheets()
elif choice == "Analysis Via File Upload":
    file_upload.analyze_file_upload()
elif choice == "Results":
    results.show_results()
elif choice == "AI Summarization":
    llm_summarization.show_summarization()
elif choice == "Export Charts":
    chart_export.show_chart_export()
elif choice == "Generate Reports":
    report_generation.show_report_generation()