import streamlit as st
import pandas as pd
import base64
import os
import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

def show_report_generation():
    """
    Display the report generation interface with a simpler implementation.
    """
    st.title("Generate and Export Reports")

    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.warning("No analysis results found. Please run an analysis first.")
        return

    try:
        # Load results
        df = pd.read_csv(results_path)

        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(5))

        # Report title and author
        st.subheader("Report Information")
        report_title = st.text_input("Report Title", "Amazon Review Sentiment Analysis Report")
        report_author = st.text_input("Report Author", "Sentiment Analysis System")

        # Generate report button
        if st.button("Generate HTML Report"):
            with st.spinner("Generating report..."):
                # Generate the report HTML
                report_html = generate_simple_html_report(df, report_title, report_author)
                
                # Create a download link
                b64_html = base64.b64encode(report_html.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64_html}" download="sentiment_report_{datetime.datetime.now().strftime("%Y%m%d")}.html">Download HTML Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.success("Report generated! Click the link above to download.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def generate_simple_html_report(df, title, author):
    """
    Generate a simple HTML report from analysis results.
    """
    # Get current date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Generate summary statistics
    total_reviews = len(df)
    sentiment_counts = df["Sentiment"].value_counts()
    
    # Calculate percentages
    positive_count = sentiment_counts.get("Positive", 0)
    negative_count = sentiment_counts.get("Negative", 0)
    neutral_count = sentiment_counts.get("Neutral", 0)
    
    positive_pct = (positive_count / total_reviews) * 100
    negative_pct = (negative_count / total_reviews) * 100
    neutral_pct = (neutral_count / total_reviews) * 100
    
    # Get top tags
    top_tags = df["Tag"].value_counts().head(5)
    
    # Generate simple charts as base64
    sentiment_pie_chart = generate_simple_pie_chart(
        [positive_count, negative_count, neutral_count],
        ["Positive", "Negative", "Neutral"],
        "Sentiment Distribution"
    )
    
    tag_bar_chart = generate_simple_bar_chart(
        top_tags.index.tolist(),
        top_tags.values.tolist(),
        "Top 5 Tags"
    )
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ margin-bottom: 30px; }}
            .chart-container {{ margin: 20px 0; text-align: center; }}
            .chart {{ max-width: 100%; height: auto; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
            <p>Generated on {current_date} by {author}</p>
        </div>
        
        <h2>Executive Summary</h2>
        <p>Analysis of {total_reviews} customer reviews reveals the following insights:</p>
        <ul>
            <li><strong>{positive_pct:.1f}%</strong> of reviews express positive sentiment ({positive_count} reviews)</li>
            <li><strong>{neutral_pct:.1f}%</strong> of reviews express neutral sentiment ({neutral_count} reviews)</li>
            <li><strong>{negative_pct:.1f}%</strong> of reviews express negative sentiment ({negative_count} reviews)</li>
        </ul>
        
        <div class="chart-container">
            <h3>Sentiment Distribution</h3>
            <img class="chart" src="data:image/png;base64,{sentiment_pie_chart}" alt="Sentiment Distribution">
        </div>
        
        <div class="chart-container">
            <h3>Top 5 Tags</h3>
            <img class="chart" src="data:image/png;base64,{tag_bar_chart}" alt="Top 5 Tags">
        </div>
        
        <h3>Top Tags Analysis</h3>
        <table>
            <tr>
                <th>Tag</th>
                <th>Count</th>
                <th>Positive</th>
                <th>Neutral</th>
                <th>Negative</th>
            </tr>
    """
    
    # Add tag analysis rows
    for tag in top_tags.index:
        tag_df = df[df["Tag"] == tag]
        tag_sentiment = tag_df["Sentiment"].value_counts()
        
        html_content += f"""
            <tr>
                <td>{tag}</td>
                <td>{len(tag_df)}</td>
                <td>{tag_sentiment.get("Positive", 0)}</td>
                <td>{tag_sentiment.get("Neutral", 0)}</td>
                <td>{tag_sentiment.get("Negative", 0)}</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <div class="footer">
            <p>Generated by Amazon Review Sentiment Analysis System</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def generate_simple_pie_chart(values, labels, title):
    """Generate a simple pie chart and return as base64 string."""
    plt.figure(figsize=(8, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title(title)
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def generate_simple_bar_chart(x, y, title):
    """Generate a simple bar chart and return as base64 string."""
    plt.figure(figsize=(10, 6))
    sns.barplot(x=x, y=y)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str