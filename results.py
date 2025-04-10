import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from visualization import (
    create_sentiment_pie_chart, 
    create_histogram, 
    create_scatter_plot,
    create_tag_bar_chart,
    create_sentiment_by_tag
)
from style import custom_warning, custom_error

def metric_card(title, value, color):
    """Display a metric in a colorful card"""
    colors = {
        "blue": "#0077b6",
        "green": "#28a745",
        "gray": "#6c757d",
        "red": "#dc3545"
    }
    
    background_color = colors.get(color, "#0077b6")
    
    html = f"""
    <div style="padding: 15px; background-color: {background_color}; border-radius: 5px; color: white;">
        <h3 style="margin: 0 0 10px 0; font-size: 1.2rem;">{title}</h3>
        <p style="font-size: 1.8rem; margin: 0; font-weight: bold;">{value}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def show_results():
    """Display and visualize the analysis results with improved UI."""
    st.title("📊 Results Dashboard")
    
    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.markdown("""
        <div style="padding: 20px; background-color: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
            <h3 style="color: #856404;">No Results Found</h3>
            <p>No analysis results have been generated yet. Please run an analysis first using either Google Sheets or File Upload.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    try:
        # Load results
        df = pd.read_csv(results_path)
        
        # Summary metrics row
        st.subheader("Summary Metrics")
        
        # Count metrics in colorful cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_reviews = len(df)
        positive_count = len(df[df["Sentiment"] == "Positive"])
        negative_count = len(df[df["Sentiment"] == "Negative"])
        neutral_count = len(df[df["Sentiment"] == "Neutral"])
        
        positive_pct = (positive_count / total_reviews) * 100
        negative_pct = (negative_count / total_reviews) * 100
        neutral_pct = (neutral_count / total_reviews) * 100
        
        with col1:
            metric_card("Total Reviews", total_reviews, "blue")
        
        with col2:
            metric_card("Positive", f"{positive_count} ({positive_pct:.1f}%)", "green")
        
        with col3:
            metric_card("Neutral", f"{neutral_count} ({neutral_pct:.1f}%)", "gray")
        
        with col4:
            metric_card("Negative", f"{negative_count} ({negative_pct:.1f}%)", "red")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Visualizations", "🔍 Data Explorer", "🏷️ Tag Analysis"])
        
        with tab1:
            # Visualization options
            st.subheader("Visualization Gallery")
            
            # First row of charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment distribution pie chart
                fig = create_sentiment_pie_chart(df)
                fig.update_layout(
                    title="Sentiment Distribution",
                    height=400,
                    margin=dict(t=50, b=50, l=10, r=10),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Tag distribution bar chart
                fig = create_tag_bar_chart(df)
                fig.update_layout(
                    title="Top Tags",
                    height=400,
                    margin=dict(t=50, b=100, l=10, r=10),
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Second row - one wider chart
            fig = create_sentiment_by_tag(df)
            fig.update_layout(
                title="Sentiment Distribution by Tag",
                height=500,
                margin=dict(t=50, b=100, l=10, r=10),
                xaxis=dict(tickangle=45)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional visualizations section - expandable
            with st.expander("Additional Visualizations"):
                viz_type = st.selectbox(
                    "Choose Visualization Type",
                    ["Histogram", "Scatter Plot", "Word Cloud"]
                )
                
                if viz_type == "Histogram":
                    column = st.selectbox("Choose column for histogram", df.columns)
                    if column:
                        fig = create_histogram(df, column)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                elif viz_type == "Scatter Plot":
                    x_column = st.selectbox("Choose X-axis column", df.columns)
                    if x_column:
                        fig = create_scatter_plot(df, x_column)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Word Cloud":
                    st.info("Word Cloud visualization requires additional setup. Coming soon!")
        
        with tab2:
            # Data exploration interface
            st.subheader("Data Explorer")
            
            # Search and filter section
            col1, col2 = st.columns([1, 1])
            
            with col1:
                search_term = st.text_input("Search in reviews:", "")
            
            with col2:
                sentiment_filter = st.multiselect(
                    "Filter by sentiment:",
                    options=["Positive", "Neutral", "Negative"],
                    default=[]
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            # Text search filter
            if search_term:
                # Find the text column (first column that's not Sentiment or Tag)
                text_column = [col for col in filtered_df.columns if col not in ["Sentiment", "Tag"]][0]
                filtered_df = filtered_df[filtered_df[text_column].str.contains(search_term, case=False, na=False)]
            
            # Sentiment filter
            if sentiment_filter:
                filtered_df = filtered_df[filtered_df["Sentiment"].isin(sentiment_filter)]
            
            # Show filtered data
            st.write(f"Showing {len(filtered_df)} of {len(df)} reviews")
            st.dataframe(filtered_df, height=400)
            
            # Export filtered data
            if len(filtered_df) > 0:
                st.download_button(
                    "Export Filtered Data",
                    filtered_df.to_csv(index=False),
                    file_name="filtered_results.csv",
                    mime="text/csv"
                )
        
        with tab3:
            # Tag analysis view
            st.subheader("Tag Analysis")
            
            if "Tag" in df.columns:
                # Get unique tags
                unique_tags = sorted(df["Tag"].unique())
                
                # Tag selector
                selected_tag = st.selectbox(
                    "Select a tag to analyze:", 
                    ["All Tags"] + list(unique_tags)
                )
                
                if selected_tag != "All Tags":
                    # Filter by selected tag
                    tag_df = df[df["Tag"] == selected_tag]
                    
                    # Display tag metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Reviews with this tag", 
                            len(tag_df),
                            delta=f"{(len(tag_df)/len(df))*100:.1f}% of total"
                        )
                    
                    with col2:
                        tag_positive = len(tag_df[tag_df["Sentiment"] == "Positive"])
                        tag_positive_pct = (tag_positive / len(tag_df)) * 100 if len(tag_df) > 0 else 0
                        st.metric(
                            "Positive Reviews", 
                            f"{tag_positive} ({tag_positive_pct:.1f}%)",
                            delta=f"{tag_positive_pct - positive_pct:.1f}%" if tag_positive_pct - positive_pct != 0 else None,
                            delta_color="normal"
                        )
                    
                    with col3:
                        tag_negative = len(tag_df[tag_df["Sentiment"] == "Negative"])
                        tag_negative_pct = (tag_negative / len(tag_df)) * 100 if len(tag_df) > 0 else 0
                        st.metric(
                            "Negative Reviews", 
                            f"{tag_negative} ({tag_negative_pct:.1f}%)",
                            delta=f"{tag_negative_pct - negative_pct:.1f}%" if tag_negative_pct - negative_pct != 0 else None,
                            delta_color="inverse"
                        )
                    
                    # Tag sentiment distribution
                    st.subheader(f"Sentiment Distribution for '{selected_tag}'")
                    
                    # Create the sentiment distribution chart for this tag
                    tag_sentiment_counts = tag_df["Sentiment"].value_counts().reset_index()
                    tag_sentiment_counts.columns = ["Sentiment", "Count"]
                    
                    colors = {
                        "Positive": "#28a745", 
                        "Neutral": "#6c757d", 
                        "Negative": "#dc3545"
                    }
                    
                    fig = px.pie(
                        tag_sentiment_counts, 
                        values="Count", 
                        names="Sentiment", 
                        title=f"Sentiment Distribution for '{selected_tag}'",
                        color="Sentiment",
                        color_discrete_map=colors
                    )
                    
                    fig.update_layout(
                        height=400,
                        margin=dict(t=50, b=50, l=10, r=10)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
    except Exception as e:
        st.error(f"Error loading or processing results: {e}")