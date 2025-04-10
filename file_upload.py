import streamlit as st
import pandas as pd
import os
from sentiment import analyze_dataframe_sentiment
from style import card_container, custom_success, custom_error, custom_warning
import time

def analyze_file_upload():
    """Handle file upload analysis workflow with improved UI."""
    st.title("📁 Upload & Analyze Reviews")
    
    # Instructions card
    st.markdown("""
    <div style="padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #2c3e50;">Instructions</h3>
        <ol style="color: #34495e;">
            <li>Upload a CSV or Excel file containing Amazon reviews</li>
            <li>Specify the column name that contains the review text</li>
            <li>Click "Start Analysis" to begin processing</li>
        </ol>
        <p style="font-style: italic; margin-top: 10px; color: #7f8c8d;">
            Supported file formats: CSV, Excel (.xlsx)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section with improved styling
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file (CSV or Excel)", 
            type=['csv', 'xlsx'],
            help="Upload a file containing Amazon reviews to analyze"
        )
    
    with col2:
        st.markdown("""
        <div style="background-color: #e8f4fc; padding: 15px; border-radius: 5px; height: 90%;">
            <h4 style="color: #2980b9;">File Requirements</h4>
            <p>Your file should have a column containing review text.</p>
            <p>Example columns: "ReviewText", "Comments", "Feedback"</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Column selection with validation
    if uploaded_file:
        try:
            # Preview the uploaded file
            st.subheader("File Preview")
            
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                
            # Show a preview of the data
            st.dataframe(df.head(5))
            
            # Column selection with suggestions
            column_options = df.columns.tolist()
            text_column_guess = next((col for col in column_options if 'review' in col.lower() or 'text' in col.lower() or 'comment' in col.lower()), column_options[0])
            
            column_name = st.selectbox(
                "Select the column containing review text:", 
                options=column_options,
                index=column_options.index(text_column_guess) if text_column_guess in column_options else 0
            )
            
            # Analysis button with improved styling and progress indicator
            if st.button("🚀 Start Analysis", key="start_analysis_btn"):
                if not column_name:
                    custom_error("Please select a column to analyze.")
                    return
                
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Simulate progress for better UX
                    for i in range(101):
                        # Update progress bar and status message
                        progress_bar.progress(i)
                        
                        if i < 20:
                            status_text.text("Reading file data...")
                        elif i < 40:
                            status_text.text("Preprocessing review text...")
                        elif i < 70:
                            status_text.text("Analyzing sentiment...")
                        elif i < 90:
                            status_text.text("Generating tags...")
                        else:
                            status_text.text("Finalizing results...")
                            
                        time.sleep(0.02)  # Add a small delay for visual effect
                    
                    # Actual analysis
                    result_df = analyze_dataframe_sentiment(df, column_name)
                    
                    # Save results
                    os.makedirs('data', exist_ok=True)
                    results_path = "data/results.csv"
                    result_df.to_csv(results_path, index=False)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display success message and preview results
                    custom_success("✅ Sentiment analysis completed successfully!")
                    
                    # Results summary
                    st.subheader("Analysis Summary")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Total Reviews", 
                            len(result_df),
                            delta=None
                        )
                    
                    with col2:
                        positive_count = len(result_df[result_df["Sentiment"] == "Positive"])
                        positive_pct = (positive_count / len(result_df)) * 100
                        st.metric(
                            "Positive Reviews", 
                            f"{positive_count} ({positive_pct:.1f}%)", 
                            delta=None
                        )
                    
                    with col3:
                        negative_count = len(result_df[result_df["Sentiment"] == "Negative"])
                        negative_pct = (negative_count / len(result_df)) * 100
                        st.metric(
                            "Negative Reviews", 
                            f"{negative_count} ({negative_pct:.1f}%)",
                            delta=None
                        )
                    
                    # Results preview
                    st.subheader("Results Preview")
                    st.dataframe(result_df.head(100))
                    
                    # Provide download button
                    st.download_button(
                        label="📥 Download Complete Results",
                        data=result_df.to_csv(index=False),
                        file_name="file_upload_analysis_results.csv",
                        mime="text/csv"
                    )
                    
                    # Next steps guidance
                    st.markdown("""
                    <div style="padding: 15px; background-color: #e8f4fc; border-radius: 5px; margin-top: 20px;">
                        <h4 style="color: #2980b9;">Next Steps</h4>
                        <p>Visit the <b>Results Dashboard</b> to visualize your analysis or use <b>AI Summarization</b> for deeper insights.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    custom_error(f"An error occurred during analysis: {str(e)}")
                
        except Exception as e:
            custom_error(f"Error reading file: {str(e)}")
    else:
        # Display example format when no file is uploaded
        st.markdown("""
        <div style="text-align: center; padding: 30px; background-color: #f8f9fa; border-radius: 10px; margin-top: 20px;">
            <h4 style="color: #7f8c8d;">No File Uploaded</h4>
            <p>Upload a file to begin sentiment analysis</p>
        </div>
        """, unsafe_allow_html=True)