import streamlit as st
import pandas as pd
import os
import openai
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

def summarize_reviews(reviews, prompt_template):
    """
    Use OpenAI to summarize a batch of reviews.
    
    Args:
        reviews (list): List of review texts
        prompt_template (str): Template for the prompt to be sent to OpenAI
    
    Returns:
        str: Generated summary
    """
    client = setup_openai_client()
    if not client:
        return "Error: OpenAI API key not set"
    
    # Join reviews with line breaks for better context
    reviews_text = "\n\n".join(map(str, reviews))

    
    # Format the prompt
    prompt = prompt_template.format(reviews=reviews_text)
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or gpt-4 if available
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes Amazon product reviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )
        
        # Return the generated summary
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def summarize_by_sentiment(df, sentiment=None):
    """
    Summarize reviews by sentiment.
    
    Args:
        df (DataFrame): DataFrame containing reviews
        sentiment (str, optional): Filter by specific sentiment ("Positive", "Negative", "Neutral")
    
    Returns:
        str: Generated summary
    """
    # Filter by sentiment if specified
    if sentiment:
        filtered_df = df[df["Sentiment"] == sentiment]
    else:
        filtered_df = df
    
    # Check if there are any reviews after filtering
    if len(filtered_df) == 0:
        return f"No {sentiment.lower() if sentiment else ''} reviews found."
    
    # Get review text column (assuming it's the first column that's not Sentiment or Tag)
    text_column = [col for col in filtered_df.columns if col not in ["Sentiment", "Tag"]][0]
    
    # Sample up to 50 reviews for summarization (to avoid API limits)
    sample_reviews = filtered_df[text_column].sample(min(50, len(filtered_df))).tolist()
    
    # Create prompt template
    sentiment_info = f" for {sentiment.lower()} reviews" if sentiment else ""
    prompt_template = f"""Please provide a concise summary{sentiment_info} of these Amazon product reviews. 
    Focus on common themes, highlight the most frequent mentions, and provide quantitative observations when possible.
    
    Reviews to summarize:
    {{reviews}}
    
    Please structure your summary to include:
    1. Overview of the main feedback points
    2. Common positive aspects mentioned
    3. Common issues or criticisms raised
    4. Suggestions or recurring requests from customers
    """
    
    return summarize_reviews(sample_reviews, prompt_template)

def summarize_by_tag(df, tag):
    """
    Summarize reviews by specific tag.
    
    Args:
        df (DataFrame): DataFrame containing reviews
        tag (str): Tag to filter by
    
    Returns:
        str: Generated summary
    """
    # Filter by tag
    filtered_df = df[df["Tag"] == tag]
    
    # Check if there are any reviews with this tag
    if len(filtered_df) == 0:
        return f"No reviews found with tag '{tag}'."
    
    # Get review text column (assuming it's the first column that's not Sentiment or Tag)
    text_column = [col for col in filtered_df.columns if col not in ["Sentiment", "Tag"]][0]
    
    # Sample up to 50 reviews for summarization (to avoid API limits)
    sample_reviews = filtered_df[text_column].sample(min(50, len(filtered_df))).tolist()
    
    # Create prompt template
    prompt_template = f"""Please provide a concise summary of these Amazon product reviews related to '{tag}'.
    Focus on common themes, highlight the most frequent mentions, and provide quantitative observations when possible.
    
    Reviews to summarize:
    {{reviews}}
    
    Please structure your summary to include:
    1. Overview of the main feedback related to {tag}
    2. Common positive aspects mentioned
    3. Common issues or criticisms raised
    4. Suggestions or recurring requests from customers
    """
    
    return summarize_reviews(sample_reviews, prompt_template)

def show_summarization():
    """
    Display the summarization interface.
    """
    st.title("Review Summarization with AI")
    
    # API Key Input
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    
    api_key = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        value=st.session_state.openai_api_key
    )
    
    if api_key:
        st.session_state.openai_api_key = api_key
    
    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.warning("No results file found. Please run an analysis first.")
        return
    
    try:
        # Load results
        df = pd.read_csv(results_path)
        
        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(5))
        
        # Summarization options
        st.subheader("Summary Options")
        summary_type = st.radio(
            "Select summary type:",
            ["All Reviews", "By Sentiment", "By Tag"]
        )
        
        if st.session_state.openai_api_key:
            if summary_type == "All Reviews":
                if st.button("Generate Overall Summary"):
                    with st.spinner("Generating summary..."):
                        summary = summarize_by_sentiment(df)
                        st.subheader("Summary of All Reviews")
                        st.write(summary)
            
            elif summary_type == "By Sentiment":
                sentiment = st.selectbox(
                    "Choose sentiment to summarize:",
                    ["Positive", "Neutral", "Negative"]
                )
                
                if st.button(f"Generate Summary for {sentiment} Reviews"):
                    with st.spinner("Generating summary..."):
                        summary = summarize_by_sentiment(df, sentiment)
                        st.subheader(f"Summary of {sentiment} Reviews")
                        st.write(summary)
            
            elif summary_type == "By Tag":
                if "Tag" in df.columns:
                    tag = st.selectbox(
                        "Choose tag to summarize:",
                        sorted(df["Tag"].unique())
                    )
                    
                    if st.button(f"Generate Summary for '{tag}' Reviews"):
                        with st.spinner("Generating summary..."):
                            summary = summarize_by_tag(df, tag)
                            st.subheader(f"Summary of Reviews Tagged as '{tag}'")
                            st.write(summary)
                else:
                    st.error("No 'Tag' column found in the results.")
        else:
            st.warning("Please enter your OpenAI API key to generate summaries.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")