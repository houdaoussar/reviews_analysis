import plotly.express as px
import streamlit as st
import pandas as pd

def create_sentiment_pie_chart(df):
    """
    Create a pie chart of sentiment distribution.
    Returns: Plotly figure
    """
    pos_percentage = (len(df[df["Sentiment"] == "Positive"])/len(df))*100
    neg_percentage = (len(df[df["Sentiment"] == "Negative"])/len(df))*100
    neu_percentage = (len(df[df["Sentiment"] == "Neutral"])/len(df))*100

    fig = px.pie(
        values=[pos_percentage, neg_percentage, neu_percentage], 
        names=["Positive", "Negative", "Neutral"],
        title="Sentiment Distribution"
    )
    return fig

def create_tag_bar_chart(df):
    """
    Create a bar chart of tag distribution.
    Returns: Plotly figure
    """
    tag_counts = df['Tag'].value_counts().reset_index()
    tag_counts.columns = ['Tag', 'Count']
    
    fig = px.bar(
        tag_counts, 
        x='Tag', 
        y='Count',
        title="Tag Distribution",
        color='Tag'
    )
    fig.update_layout(xaxis_title="Tag Category", yaxis_title="Count")
    return fig

def create_sentiment_by_tag(df):
    """
    Create a stacked bar chart showing sentiment distribution by tag.
    Returns: Plotly figure
    """
    # Group by Tag and Sentiment and get counts
    grouped = df.groupby(['Tag', 'Sentiment']).size().reset_index(name='Count')
    
    fig = px.bar(
        grouped, 
        x='Tag', 
        y='Count', 
        color='Sentiment', 
        title="Sentiment Distribution by Tag",
        color_discrete_map={
            'Positive': 'green',
            'Neutral': 'gray',
            'Negative': 'red'
        }
    )
    fig.update_layout(xaxis_title="Tag Category", yaxis_title="Count")
    return fig

def create_histogram(df, column_name):
    """
    Create a histogram for a specific column, colored by sentiment.
    Returns: Plotly figure
    """
    fig = px.histogram(df, x=column_name, color="Sentiment")
    fig.update_layout(yaxis_title="Count", xaxis_title=column_name)
    return fig

def create_scatter_plot(df, x_column):
    """
    Create a scatter plot with x_column vs Sentiment.
    Returns: Plotly figure
    """
    fig = px.scatter(df, x=x_column, y="Sentiment")
    fig.update_layout(xaxis_title=x_column, yaxis_title="Sentiment")
    return fig