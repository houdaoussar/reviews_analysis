from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import pandas as pd
from tagging import suggest_tag

# Initialize the sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()
huggingface_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased")

def analyze_sentiment_vader(text):
    """
    Analyze sentiment using VADER.
    Returns: "Positive", "Negative", or "Neutral"
    """
    pred = vader_analyzer.polarity_scores(str(text))
    if pred['compound'] > 0.5:
        return "Positive"
    elif pred['compound'] < -0.5:
        return "Negative"
    else:
        return "Neutral"

def analyze_dataframe_sentiment(df, column_name):
    """
    Analyze sentiment for a specific column in a dataframe.
    Returns: The dataframe with added 'Sentiment' and 'Tag' columns
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in dataframe")
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Apply sentiment analysis to each row
    result_df['Sentiment'] = result_df[column_name].apply(analyze_sentiment_vader)
    
    # Apply tag suggestion to each row
    result_df['Tag'] = result_df[column_name].apply(suggest_tag)
    
    return result_df