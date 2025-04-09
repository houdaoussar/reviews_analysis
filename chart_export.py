import streamlit as st
import pandas as pd
import os
import plotly.io as pio
import base64
from io import BytesIO
import datetime
from visualization import (
    create_sentiment_pie_chart, 
    create_tag_bar_chart,
    create_sentiment_by_tag,
    create_histogram,
    create_scatter_plot
)

def show_chart_export():
    """
    Display the chart export interface.
    """
    st.title("Export Charts as Images")
    
    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.warning("No analysis results found. Please run an analysis first.")
        return
    
    try:
        # Load results
        df = pd.read_csv(results_path)
        
        # Chart selection
        st.subheader("Select Chart to Export")
        chart_type = st.selectbox(
            "Chart Type",
            [
                "Sentiment Distribution (Pie Chart)",
                "Tag Distribution (Bar Chart)",
                "Sentiment by Tag (Stacked Bar Chart)",
                "Custom Histogram",
                "Custom Scatter Plot"
            ]
        )
        
        # Based on selection, generate chart
        fig = None
        if chart_type == "Sentiment Distribution (Pie Chart)":
            fig = create_sentiment_pie_chart(df)
            
        elif chart_type == "Tag Distribution (Bar Chart)":
            fig = create_tag_bar_chart(df)
            
        elif chart_type == "Sentiment by Tag (Stacked Bar Chart)":
            fig = create_sentiment_by_tag(df)
            
        elif chart_type == "Custom Histogram":
            column = st.selectbox("Choose column for histogram", df.columns)
            if column:
                fig = create_histogram(df, column)
                
        elif chart_type == "Custom Scatter Plot":
            x_column = st.selectbox("Choose X-axis column", df.columns)
            if x_column:
                fig = create_scatter_plot(df, x_column)
        
        # Display chart preview
        if fig:
            st.subheader("Chart Preview")
            st.plotly_chart(fig)
            
            # Export options
            st.subheader("Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                format_type = st.selectbox("File Format", ["PNG", "SVG", "JPEG", "PDF"])
            
            with col2:
                width = st.number_input("Width (pixels)", min_value=400, max_value=2000, value=800)
                height = st.number_input("Height (pixels)", min_value=300, max_value=1500, value=600)
            
            # Export button
            if st.button("Export Chart"):
                with st.spinner("Exporting chart..."):
                    # Generate filename
                    chart_name = chart_type.split(" (")[0].replace(" ", "_").lower()
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{chart_name}_{timestamp}.{format_type.lower()}"
                    
                    # Export chart
                    img_bytes = export_chart(fig, format_type.lower(), width, height)
                    
                    # Provide download button
                    mime_type = f"image/{format_type.lower()}"
                    if format_type.lower() == "pdf":
                        mime_type = "application/pdf"
                    
                    st.success(f"{format_type} chart generated!")
                    st.download_button(
                        label=f"Download {format_type}",
                        data=img_bytes,
                        file_name=filename,
                        mime=mime_type
                    )
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def export_chart(fig, format_type, width, height):
    """
    Export a Plotly figure as an image.
    
    Args:
        fig: The Plotly figure to export
        format_type: The image format (png, svg, jpeg, pdf)
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        bytes: The image as bytes
    """
    # Set the figure size
    fig.update_layout(
        width=width,
        height=height
    )
    
    # Export to the specified format
    img_bytes = pio.to_image(fig, format=format_type, scale=2)
    
    return img_bytes