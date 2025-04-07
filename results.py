import streamlit as st
import pandas as pd
import os
import plotly.express as px
from visualization import (
    create_sentiment_pie_chart, 
    create_histogram, 
    create_scatter_plot,
    create_tag_bar_chart,
    create_sentiment_by_tag
)

def show_results():
    """Display and visualize the analysis results."""
    st.title("Results")
    
    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.warning("No results file found. Please run an analysis first.")
        return
    
    try:
        # Load results
        df = pd.read_csv(results_path)
        
        # Display the data
        st.dataframe(df)
        
        # Visualization options
        choice = st.selectbox("Choose Visualization", (
            "None", 
            "Sentiment Pie Chart", 
            "Tag Distribution", 
            "Sentiment by Tag", 
            "Histogram", 
            "Scatter Plot"
        ))
        
        if choice == "Sentiment Pie Chart":
            fig = create_sentiment_pie_chart(df)
            st.plotly_chart(fig)
            
        elif choice == "Tag Distribution":
            fig = create_tag_bar_chart(df)
            st.plotly_chart(fig)
            
        elif choice == "Sentiment by Tag":
            fig = create_sentiment_by_tag(df)
            st.plotly_chart(fig)
            
        elif choice == "Histogram":
            column = st.selectbox("Choose column", df.columns)
            if column:
                fig = create_histogram(df, column)
                st.plotly_chart(fig)
                
        elif choice == "Scatter Plot":
            x_column = st.selectbox("Choose column x", df.columns)
            if x_column:
                fig = create_scatter_plot(df, x_column)
                st.plotly_chart(fig)
        
        # Tag filtering
        st.subheader("Filter by Tag")
        if "Tag" in df.columns:
            selected_tag = st.selectbox("Select a tag to filter results", 
                                       ["All Tags"] + list(df["Tag"].unique()))
            
            if selected_tag != "All Tags":
                filtered_df = df[df["Tag"] == selected_tag]
                st.write(f"Showing {len(filtered_df)} reviews tagged as '{selected_tag}'")
                st.dataframe(filtered_df)
                
                # Sentiment distribution for selected tag
                tag_sentiment_counts = filtered_df["Sentiment"].value_counts().reset_index()
                tag_sentiment_counts.columns = ["Sentiment", "Count"]
                
                fig = px.pie(
                    tag_sentiment_counts, 
                    values="Count", 
                    names="Sentiment", 
                    title=f"Sentiment Distribution for '{selected_tag}'"
                )
                st.plotly_chart(fig)
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")