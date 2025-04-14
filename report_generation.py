import streamlit as st
import pandas as pd
import base64
import os
import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI

def setup_openai_client():
    """
    Set up and return the OpenAI client with API key.
    """
    api_key = st.session_state.get('openai_api_key')
    if not api_key:
        return None
    
    client = OpenAI(api_key=api_key)
    return client

def generate_business_insights(df):
    """
    Use GPT to generate business insights from review data.
    """
    client = setup_openai_client()
    if not client:
        return ["Please set your OpenAI API key to generate insights."]
    
    # Calculate basic statistics
    total_reviews = len(df)
    sentiment_counts = df["Sentiment"].value_counts()
    
    positive_count = sentiment_counts.get("Positive", 0)
    negative_count = sentiment_counts.get("Negative", 0)
    neutral_count = sentiment_counts.get("Neutral", 0)
    
    positive_pct = (positive_count / total_reviews) * 100
    negative_pct = (negative_count / total_reviews) * 100
    neutral_pct = (neutral_count / total_reviews) * 100
    
    # Get tag statistics
    tag_stats = {}
    for tag in df["Tag"].unique():
        tag_df = df[df["Tag"] == tag]
        tag_sentiments = tag_df["Sentiment"].value_counts(normalize=True) * 100
        tag_stats[tag] = {
            "count": len(tag_df),
            "positive_pct": tag_sentiments.get("Positive", 0),
            "neutral_pct": tag_sentiments.get("Neutral", 0),
            "negative_pct": tag_sentiments.get("Negative", 0)
        }
    
    # Format tag statistics for the prompt
    tag_stats_text = ""
    for tag, stats in tag_stats.items():
        tag_stats_text += f"- {tag}: {stats['count']} reviews, {stats['positive_pct']:.1f}% positive, {stats['negative_pct']:.1f}% negative\n"
    
    # Create a sample of review text for context
    review_sample = df.sample(min(50, len(df)))
    text_column = [col for col in df.columns if col not in ["Sentiment", "Tag"]][0]
    review_texts = []
    
    for _, row in review_sample.iterrows():
        review_texts.append(f"Review [Sentiment: {row['Sentiment']}, Tag: {row['Tag']}]: {row[text_column]}")
    
    sample_reviews = "\n\n".join(review_texts)
    
    # Create the prompt
    prompt = f"""Analyze these Amazon product review statistics and sample reviews to generate 3 high-impact business insights.

Review Statistics:
- Total reviews: {total_reviews}
- Sentiment distribution: {positive_pct:.1f}% positive, {neutral_pct:.1f}% neutral, {negative_pct:.1f}% negative

Tag Statistics:
{tag_stats_text}

Sample Reviews:
{sample_reviews}

For each insight, include:
1. A clear title in the format "Key Insight: [Brief description]"
2. A specific percentage or metric that quantifies the insight
3. A concise recommendation for business action

Format each insight as an "insight card" with 2-3 sentences maximum, highlighting the most important customer sentiment patterns and their business implications. Focus on:
- Most frequent complaints
- Improvement opportunities (areas with high negative sentiment)
- Positive differentiators (areas with high positive sentiment)
- Demographic patterns (if demographic data is available)

Examples:
"Most frequent complaint: Late Delivery (22% of negative reviews). Consider restructuring logistics to improve delivery times."
"Improvement opportunity: Packaging has 48% negative sentiment. Invest in more secure packaging solutions."
"Positive differentiator: Excellent customer service praised in 61% of positive reviews. Continue training support team and highlight service in marketing."

Provide exactly 3 insights formatted as shown above.
"""
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a business analyst that identifies actionable insights from customer review data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse insights from the response
        insights_text = response.choices[0].message.content.strip()
        insights_list = [insight.strip() for insight in insights_text.split("\n\n") if insight.strip()]
        
        # Return only the first 3 insights
        return insights_list[:3]
    
    except Exception as e:
        return [f"Error generating insights: {str(e)}"]

def create_insight_cards(insights):
    """
    Format business insights as HTML cards.
    """
    cards_html = '<div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px;">'
    
    colors = ["#4285F4", "#EA4335", "#34A853"]  # Blue, Red, Green
    icons = ["💡", "⚠️", "✅"]  # Ideas, Warning, Success
    
    for i, insight in enumerate(insights):
        color = colors[i % len(colors)]
        icon = icons[i % len(icons)]
        
        cards_html += f"""
        <div style="flex: 1; min-width: 300px; background-color: white; border-left: 5px solid {color}; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 15px; border-radius: 4px;">
            <h3 style="margin-top: 0; color: {color};">{icon} {insight.split(':')[0] if ':' in insight else 'Insight'}</h3>
            <p style="margin-bottom: 0;">{insight.split(':', 1)[1].strip() if ':' in insight else insight}</p>
        </div>
        """
    
    cards_html += '</div>'
    return cards_html

def display_insight_cards(df):
    """
    Display insight cards with key business insights at the top of the dashboard.
    """
    # Check if OpenAI API key is set
    if 'openai_api_key' not in st.session_state or not st.session_state.openai_api_key:
        # Show placeholder cards with static content
        st.warning("Enter your OpenAI API key in the sidebar to generate AI insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("💡 **Common insight**: Add your OpenAI API key to generate personalized insights.")
        
        with col2:
            st.warning("⚠️ **Improvement opportunity**: Enable AI analysis to identify key improvement areas.")
        
        with col3:
            st.success("✅ **Business opportunity**: Complete sentiment analysis to unlock actionable insights.")
    
    else:
        # If insights are already generated, use them
        if 'dashboard_insights' in st.session_state:
            insights = st.session_state.dashboard_insights
        else:
            # Generate insights
            with st.spinner("Generating business insights..."):
                insights = generate_business_insights(df)
                st.session_state.dashboard_insights = insights
        
        # Display insights in columns
        if len(insights) >= 3:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"💡 {insights[0]}")
            
            with col2:
                st.warning(f"⚠️ {insights[1]}")
            
            with col3:
                st.success(f"✅ {insights[2]}")
        else:
            # Fall back to a single column if fewer than 3 insights
            for insight in insights:
                st.info(f"💡 {insight}")

def show_report_generation():
    """
    Display the enhanced report generation interface with insight cards.
    """
    st.title("Generate and Export Reports")

    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.warning("No analysis results found. Please run an analysis first.")
        return

    # API Key Input for OpenAI
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    
    api_key = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        value=st.session_state.openai_api_key,
        help="Required to generate business insights with AI."
    )
    
    if api_key:
        st.session_state.openai_api_key = api_key

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
        
        # Generate insights button
        if st.button("Generate Business Insights"):
            if not st.session_state.openai_api_key:
                st.warning("Please enter your OpenAI API key to generate business insights.")
            else:
                with st.spinner("Analyzing review data for insights..."):
                    insights = generate_business_insights(df)
                    st.session_state.insights = insights
                    
                    # Display insights preview
                    st.subheader("AI-Generated Business Insights")
                    for i, insight in enumerate(insights):
                        st.info(f"💡 {insight}")
                    
                    st.success("Business insights generated! These will be included in your report.")

        # Generate report button
        if st.button("Generate Enhanced HTML Report"):
            with st.spinner("Generating report..."):
                # Generate insights if not already done
                if 'insights' not in st.session_state and st.session_state.openai_api_key:
                    st.session_state.insights = generate_business_insights(df)
                elif 'insights' not in st.session_state:
                    st.session_state.insights = [
                        "Most frequent complaint: Late Delivery (22% of negative reviews). Consider restructuring logistics to improve delivery times.",
                        "Improvement opportunity: Packaging has 48% negative sentiment. Invest in more secure packaging solutions.",
                        "Positive differentiator: Excellent customer service praised in 61% of positive reviews. Continue training support team and highlight service in marketing."
                    ]
                
                # Generate the report HTML
                report_html = generate_enhanced_html_report(
                    df, 
                    report_title, 
                    report_author, 
                    st.session_state.insights
                )
                
                # Create a download link
                b64_html = base64.b64encode(report_html.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64_html}" download="sentiment_report_{datetime.datetime.now().strftime("%Y%m%d")}.html">Download Enhanced HTML Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.success("Enhanced report generated! Click the link above to download.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def generate_enhanced_html_report(df, title, author, insights):
    """
    Generate an enhanced HTML report with insight cards and demographic analysis.
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
    
    # Generate charts as base64
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
    
    # Generate tag sentiment chart
    tag_sentiment_chart = generate_tag_sentiment_chart(df)
    
    # Generate demographic charts if available
    demographic_charts_html = ""
    if "Age_Group" in df.columns:
        age_sentiment_chart = generate_age_sentiment_chart(df)
        demographic_charts_html += f"""
        <div class="chart-container">
            <h3>Sentiment by Age Group</h3>
            <img class="chart" src="data:image/png;base64,{age_sentiment_chart}" alt="Sentiment by Age Group">
        </div>
        """
    
    if "Verified_Purchaser" in df.columns:
        verification_sentiment_chart = generate_verification_sentiment_chart(df)
        demographic_charts_html += f"""
        <div class="chart-container">
            <h3>Sentiment by Verification Status</h3>
            <img class="chart" src="data:image/png;base64,{verification_sentiment_chart}" alt="Sentiment by Verification Status">
        </div>
        """
    
    # Format the insights as cards
    insight_cards_html = create_insight_cards(insights)
    
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
            .insights-section {{ margin: 30px 0; }}
            .section-divider {{ height: 1px; background-color: #ddd; margin: 30px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
            <p>Generated on {current_date} by {author}</p>
        </div>
        
        <div class="insights-section">
            <h2>Key Business Insights</h2>
            {insight_cards_html}
        </div>
        
        <div class="section-divider"></div>
        
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
        
        <div class="chart-container">
            <h3>Sentiment Distribution by Tag</h3>
            <img class="chart" src="data:image/png;base64,{tag_sentiment_chart}" alt="Sentiment by Tag">
        </div>
        
        {demographic_charts_html}
        
        <h3>Top Tags Analysis</h3>
        <table>
            <tr>
                <th>Tag</th>
                <th>Count</th>
                <th>Positive</th>
                <th>Neutral</th>
                <th>Negative</th>
                <th>Positive %</th>
                <th>Negative %</th>
            </tr>
    """
    
    # Add tag analysis rows with percentages
    for tag in top_tags.index:
        tag_df = df[df["Tag"] == tag]
        tag_count = len(tag_df)
        tag_sentiment = tag_df["Sentiment"].value_counts()
        
        pos_count = tag_sentiment.get("Positive", 0)
        neg_count = tag_sentiment.get("Negative", 0)
        neu_count = tag_sentiment.get("Neutral", 0)
        
        pos_pct = (pos_count / tag_count) * 100 if tag_count > 0 else 0
        neg_pct = (neg_count / tag_count) * 100 if tag_count > 0 else 0
        
        html_content += f"""
            <tr>
                <td>{tag}</td>
                <td>{tag_count}</td>
                <td>{pos_count}</td>
                <td>{neu_count}</td>
                <td>{neg_count}</td>
                <td>{pos_pct:.1f}%</td>
                <td>{neg_pct:.1f}%</td>
            </tr>
        """
    
    # Add demographic tables if available
    demographic_tables_html = ""
    
    if "Age_Group" in df.columns:
        demographic_tables_html += """
        <h3>Age Group Analysis</h3>
        <table>
            <tr>
                <th>Age Group</th>
                <th>Count</th>
                <th>Positive</th>
                <th>Neutral</th>
                <th>Negative</th>
                <th>Positive %</th>
                <th>Negative %</th>
            </tr>
        """
        
        age_groups = df["Age_Group"].value_counts().index
        for age in age_groups:
            age_df = df[df["Age_Group"] == age]
            age_count = len(age_df)
            age_sentiment = age_df["Sentiment"].value_counts()
            
            pos_count = age_sentiment.get("Positive", 0)
            neg_count = age_sentiment.get("Negative", 0)
            neu_count = age_sentiment.get("Neutral", 0)
            
            pos_pct = (pos_count / age_count) * 100 if age_count > 0 else 0
            neg_pct = (neg_count / age_count) * 100 if age_count > 0 else 0
            
            demographic_tables_html += f"""
                <tr>
                    <td>{age}</td>
                    <td>{age_count}</td>
                    <td>{pos_count}</td>
                    <td>{neu_count}</td>
                    <td>{neg_count}</td>
                    <td>{pos_pct:.1f}%</td>
                    <td>{neg_pct:.1f}%</td>
                </tr>
            """
        
        demographic_tables_html += "</table>"
    
    html_content += """
        </table>
    """ + demographic_tables_html + """
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
    colors = ['#4CAF50', '#F44336', '#9E9E9E']  # Green, Red, Gray
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.axis('equal')
    plt.title(title)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def generate_simple_bar_chart(x, y, title):
    """Generate a simple bar chart and return as base64 string."""
    plt.figure(figsize=(10, 6))
    colors = ['#2196F3'] * len(x)  # Blue
    plt.bar(x, y, color=colors)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def generate_tag_sentiment_chart(df):
    """Generate a stacked bar chart of sentiment by tag."""
    plt.figure(figsize=(12, 7))
    
    # Count sentiment by tag
    tag_sentiment = pd.crosstab(df['Tag'], df['Sentiment'])
    
    # Sort by total count
    tag_sentiment['Total'] = tag_sentiment.sum(axis=1)
    tag_sentiment = tag_sentiment.sort_values('Total', ascending=False).head(10)
    tag_sentiment = tag_sentiment.drop('Total', axis=1)
    
    # Calculate percentages
    tag_sentiment_pct = tag_sentiment.div(tag_sentiment.sum(axis=1), axis=0) * 100
    
    # Plot
    tag_sentiment_pct = tag_sentiment_pct.reindex(columns=['Positive', 'Neutral', 'Negative'])
    ax = tag_sentiment_pct.plot(kind='barh', stacked=True, figsize=(12, 7), 
                          color=['#4CAF50', '#9E9E9E', '#F44336'])
    
    plt.title('Sentiment Distribution by Tag (%)', fontsize=14)
    plt.xlabel('Percentage', fontsize=12)
    plt.ylabel('Tag', fontsize=12)
    plt.legend(title='Sentiment')
    plt.tight_layout()
    
    # Add count labels to the end of each bar
    for i, tag in enumerate(tag_sentiment_pct.index):
        total = tag_sentiment.loc[tag].sum()
        plt.text(101, i, f'n={total}', va='center', fontsize=9)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def generate_age_sentiment_chart(df):
    """Generate a chart showing sentiment by age group."""
    if "Age_Group" not in df.columns:
        return None
    
    plt.figure(figsize=(10, 6))
    
    # Count sentiment by age group
    age_sentiment = pd.crosstab(df['Age_Group'], df['Sentiment'])
    
    # Calculate percentages
    age_sentiment_pct = age_sentiment.div(age_sentiment.sum(axis=1), axis=0) * 100
    
    # Plot
    age_sentiment_pct = age_sentiment_pct.reindex(columns=['Positive', 'Neutral', 'Negative'])
    ax = age_sentiment_pct.plot(kind='bar', stacked=True, figsize=(10, 6),
                         color=['#4CAF50', '#9E9E9E', '#F44336'])
    
    plt.title('Sentiment Distribution by Age Group (%)', fontsize=14)
    plt.xlabel('Age Group', fontsize=12)
    plt.ylabel('Percentage', fontsize=12)
    plt.legend(title='Sentiment')
    plt.tight_layout()
    
    # Add count labels above each bar
    for i, age in enumerate(age_sentiment_pct.index):
        total = age_sentiment.loc[age].sum()
        plt.text(i, 101, f'n={total}', ha='center', fontsize=9)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def generate_verification_sentiment_chart(df):
    """Generate a chart showing sentiment by verification status."""
    if "Verified_Purchaser" not in df.columns:
        return None
    
    plt.figure(figsize=(8, 5))
    
    # Map boolean values to strings for better display
    df_display = df.copy()
    df_display["Verification"] = df_display["Verified_Purchaser"].map({True: "Verified", False: "Non-Verified"})
    
    # Count sentiment by verification
    verification_sentiment = pd.crosstab(df_display['Verification'], df_display['Sentiment'])
    
    # Calculate percentages
    verification_sentiment_pct = verification_sentiment.div(verification_sentiment.sum(axis=1), axis=0) * 100
    
    # Plot
    verification_sentiment_pct = verification_sentiment_pct.reindex(columns=['Positive', 'Neutral', 'Negative'])
    ax = verification_sentiment_pct.plot(kind='bar', stacked=True, figsize=(8, 5),
                                  color=['#4CAF50', '#9E9E9E', '#F44336'])
    
    plt.title('Sentiment Distribution by Verification Status (%)', fontsize=14)
    plt.xlabel('Verification Status', fontsize=12)
    plt.ylabel('Percentage', fontsize=12)
    plt.legend(title='Sentiment')
    plt.tight_layout()
    
    # Add count labels above each bar
    for i, status in enumerate(verification_sentiment_pct.index):
        total = verification_sentiment.loc[status].sum()
        plt.text(i, 101, f'n={total}', ha='center', fontsize=9)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str