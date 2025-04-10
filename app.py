import streamlit as st

# Configure page settings - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Amazon Sentiment Analysis System",
    page_icon="📊",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Now import other modules after the page config
import home, google_sheets, file_upload, results, llm_summarization
import report_generation, chart_export
from style import apply_custom_style, custom_warning, custom_success, custom_error

# Apply custom styling after page config
apply_custom_style()

# Add a logo or header image to the sidebar
st.sidebar.image("https://miro.medium.com/v2/1*_JW1JaMpK_fVGld8pd1_JQ.gif", width=250)

# Application title
st.sidebar.title("Amazon Review Analysis")
st.sidebar.markdown("---")

# Navigation menu with icons
choice = st.sidebar.selectbox(
    "Navigation", 
    [
        "🏠 Home", 
        "📈 Analysis Via Google Sheets", 
        "📁 Analysis Via File Upload", 
        "📊 Results Dashboard", 
        "🤖 AI Summarization",
        "📷 Export Charts",
        "📑 Generate Reports"
    ]
)

# Footer for sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    "Developed with ❤️ by Sentiment Analysis Team\n\n"
    "© 2025 All Rights Reserved"
)

# Route to the appropriate page based on user selection
if choice == "🏠 Home":
    home.show_home()
elif choice == "📈 Analysis Via Google Sheets":
    google_sheets.analyze_google_sheets()
elif choice == "📁 Analysis Via File Upload":
    file_upload.analyze_file_upload()
elif choice == "📊 Results Dashboard":
    results.show_results()
elif choice == "🤖 AI Summarization":
    llm_summarization.show_summarization()
elif choice == "📷 Export Charts":
    chart_export.show_chart_export()
elif choice == "📑 Generate Reports":
    report_generation.show_report_generation()