import streamlit as st

def show_home():
    """Display the home page."""
    st.image("https://miro.medium.com/v2/1*_JW1JaMpK_fVGld8pd1_JQ.gif")
    
    st.subheader("About this Application")
    st.write("1. It is a natural language Processing Application which can analyze the sentiment on the text data.")
    st.write("2. This application predicts the sentiment into 3 categories Positive, Negative and Neutral.")
    st.write("3. This application then visualizes the results based on different factors such as age, gender.")