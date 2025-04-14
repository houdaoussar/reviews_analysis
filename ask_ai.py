import streamlit as st
import pandas as pd
import os
import openai
from openai import OpenAI
import numpy as np
from datetime import datetime
import json
from style import custom_warning, custom_success, custom_error

def setup_openai_client():
    """
    Set up and return the OpenAI client with API key.
    """
    api_key = st.session_state.get('openai_api_key')
    if not api_key:
        return None
    
    client = OpenAI(api_key=api_key)
    return client

def get_review_insights(df, query, max_samples=100):
    """
    Process a user query against review data and return relevant insights.
    
    Args:
        df (DataFrame): DataFrame containing reviews
        query (str): User's question about the reviews
        max_samples (int): Maximum number of reviews to include in context
    
    Returns:
        str: AI-generated response to the query
    """
    client = setup_openai_client()
    if not client:
        return "Error: OpenAI API key not set"
    
    # Get text column name (first column that's not Sentiment or Tag)
    text_column = [col for col in df.columns if col not in ["Sentiment", "Tag"]][0]
    
    # Preprocess the query to identify potential filters
    query_lower = query.lower()
    
    # Determine if we need to filter by sentiment
    sentiment_filter = None
    if "positive" in query_lower and "negative" not in query_lower:
        sentiment_filter = "Positive"
    elif "negative" in query_lower and "positive" not in query_lower:
        sentiment_filter = "Negative"
    elif "neutral" in query_lower:
        sentiment_filter = "Neutral"
    
    # Determine if we need to filter by tag
    tag_filter = None
    unique_tags = df["Tag"].unique()
    for tag in unique_tags:
        if tag.lower() in query_lower:
            tag_filter = tag
            break
    
    # Apply filters if needed
    filtered_df = df.copy()
    if sentiment_filter:
        filtered_df = filtered_df[filtered_df["Sentiment"] == sentiment_filter]
    if tag_filter:
        filtered_df = filtered_df[filtered_df["Tag"] == tag_filter]
    
    # If no reviews match the filters, return a message
    if len(filtered_df) == 0:
        return f"I couldn't find any reviews matching your criteria. Please try a different question."
    
    # Sample reviews for context (to avoid token limits)
    if len(filtered_df) > max_samples:
        sampled_df = filtered_df.sample(max_samples)
    else:
        sampled_df = filtered_df
    
    # Prepare reviews for the prompt
    reviews_list = []
    for idx, row in sampled_df.iterrows():
        review_text = row[text_column]
        sentiment = row["Sentiment"]
        tag = row["Tag"]
        reviews_list.append(f"Review {idx+1} [Sentiment: {sentiment}, Tag: {tag}]: {review_text}")
    
    reviews_text = "\n\n".join(reviews_list)
    
    # Statistics to include in prompt
    stats_text = f"""
    Data Summary:
    - Total reviews in dataset: {len(df)}
    - Reviews matching filters: {len(filtered_df)}
    - Sample size used for analysis: {len(sampled_df)}
    - Sentiment distribution in filtered data: 
      - Positive: {len(filtered_df[filtered_df['Sentiment'] == 'Positive'])} ({len(filtered_df[filtered_df['Sentiment'] == 'Positive'])/len(filtered_df)*100:.1f}%)
      - Neutral: {len(filtered_df[filtered_df['Sentiment'] == 'Neutral'])} ({len(filtered_df[filtered_df['Sentiment'] == 'Neutral'])/len(filtered_df)*100:.1f}%)
      - Negative: {len(filtered_df[filtered_df['Sentiment'] == 'Negative'])} ({len(filtered_df[filtered_df['Sentiment'] == 'Negative'])/len(filtered_df)*100:.1f}%)
    - Top tags in filtered data: {', '.join(filtered_df['Tag'].value_counts().head(3).index.tolist())}
    """
    
    # Generate the prompt
    prompt = f"""You are an AI assistant that helps analyze Amazon product reviews. If any question is outside of this scope then clearly mention that role is just to analyze and inform about the reviews.

    
    USER QUERY: "{query}"
    
    {stats_text}
    
    Here is a sample of the relevant reviews:
    
    {reviews_text}
    
    Based on the reviews above, provide a thoughtful, data-driven answer to the user's query. Include:
    1. A direct answer to the question
    2. Key insights and patterns from the reviews
    3. Notable quotes or examples that illustrate your points (reference specific review numbers)
    4. Quantitative observations when possible
    
    Keep your response concise, professional, and focused on the data provided.
    """
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",  # Using a model with larger context
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes Amazon review data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        # Return the generated insight
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def save_conversation(query, response):
    """Save conversation history to session state"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.conversation_history.append({
        "timestamp": timestamp,
        "query": query,
        "response": response
    })

def clear_conversation():
    """Clear conversation history"""
    if 'conversation_history' in st.session_state:
        st.session_state.conversation_history = []

def format_chat_message(sender, message, timestamp=None):
    """Format a chat message with proper styling"""
    if sender == "user":
        return f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
            <div style="background-color: #0084ff; color: white; padding: 10px 15px; border-radius: 20px 20px 0px 20px; max-width: 80%;">
                <p style="margin: 0;">{message}</p>
                {f'<p style="margin: 0; font-size: 0.7em; text-align: right; opacity: 0.8;">{timestamp}</p>' if timestamp else ''}
            </div>
        </div>
        """
    else:  # AI response
        return f"""
        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
            <div style="background-color: #f0f2f5; color: #000; padding: 10px 15px; border-radius: 20px 20px 20px 0px; max-width: 80%;">
                <p style="margin: 0;">{message}</p>
                {f'<p style="margin: 0; font-size: 0.7em; opacity: 0.8;">{timestamp}</p>' if timestamp else ''}
            </div>
        </div>
        """

def show_ask_ai():
    """Display the Ask AI interface."""
    st.title("🤖 Ask AI About Your Reviews")
    
    # Check if results file exists
    results_path = "data/results.csv"
    if not os.path.exists(results_path):
        st.warning("No analysis results found. Please run an analysis first.")
        return
    
    # API Key Input
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    
    with st.sidebar:
        st.subheader("OpenAI API Settings")
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            value=st.session_state.openai_api_key,
            help="Required for the AI to answer your questions about reviews."
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
        
        # Add a clear conversation button
        if st.button("Clear Conversation"):
            clear_conversation()
            st.success("Conversation history cleared!")
    
    try:
        # Load the results dataframe
        df = pd.read_csv(results_path)
        
        # Quick dataset summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Reviews", len(df))
        
        with col2:
            st.metric("Positive Reviews", f"{len(df[df['Sentiment'] == 'Positive'])} ({len(df[df['Sentiment'] == 'Positive'])/len(df)*100:.1f}%)")
        
        with col3:
            st.metric("Tags", len(df["Tag"].unique()))
        
        # Example questions
        st.markdown("### Example Questions:")
        example_container = st.container()
        
        example_questions = [
            "What are customers saying about delivery times?",
            "Summarize the main complaints in negative reviews.",
            "What are people saying about the product quality?",
            "Which tag has the worst sentiment ratio?",
            "What are the common issues with fit and size?"
        ]
        
        col1, col2 = example_container.columns(2)
        
        for i, question in enumerate(example_questions):
            if i % 2 == 0:
                if col1.button(f"📝 {question}", key=f"example_{i}"):
                    st.session_state.query = question
            else:
                if col2.button(f"📝 {question}", key=f"example_{i}"):
                    st.session_state.query = question
        
        # Main chat interface
        st.markdown("---")
        
        # Initialize the query state if it doesn't exist
        if 'query' not in st.session_state:
            st.session_state.query = ""
        
        # Show conversation history
        chat_container = st.container()
        
        # Chat input at the bottom
        query = st.chat_input("Ask anything about your reviews...", key="chat_input")
        
        # Handle new query
        if query:
            st.session_state.query = query
        
        # Process the query if one exists in state
        if st.session_state.query:
            if not st.session_state.openai_api_key:
                custom_error("Please enter your OpenAI API key in the sidebar to use the Ask AI feature.")
            else:
                # Get new query from session state
                current_query = st.session_state.query
                
                # Generate response
                with st.spinner("Analyzing reviews..."):
                    response = get_review_insights(df, current_query)
                
                # Save to conversation history
                save_conversation(current_query, response)
                
                # Clear the input
                st.session_state.query = ""
        
        # Display conversation history
        with chat_container:
            if 'conversation_history' in st.session_state and st.session_state.conversation_history:
                for message in st.session_state.conversation_history:
                    # Display user message
                    st.markdown(
                        format_chat_message("user", message["query"], message["timestamp"]),
                        unsafe_allow_html=True
                    )
                    
                    # Display AI response
                    st.markdown(
                        format_chat_message("ai", message["response"]),
                        unsafe_allow_html=True
                    )
            else:
                # Display welcome message
                st.markdown("""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; margin: 40px 0;">
                    <h3>Welcome to Ask AI! 👋</h3>
                    <p>Ask me anything about your review data. I can help you understand sentiment patterns, identify common issues, extract insights, and more.</p>
                    <p style="font-style: italic;">Try one of the example questions above or type your own question below.</p>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        
    # Tips and documentation
    with st.expander("📚 Tips for asking good questions"):
        st.markdown("""
        ### Tips for effective questions:
        
        - **Be specific** - "What do customers like about the product?" is better than "What's good?"
        - **Target specific segments** - Try "What are negative reviews saying about delivery?" to focus on a specific issue
        - **Ask for comparisons** - "How do positive and negative reviews differ in their mentions of customer service?"
        - **Request data points** - "What percentage of reviews mention size issues?" will get you quantitative insights
        - **Ask about trends** - "What are the most common complaints in negative reviews?"
        
        The AI can analyze sentiment, extract common themes, identify patterns, and provide summaries of your review data.
        """)