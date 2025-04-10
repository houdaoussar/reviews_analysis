import streamlit as st
from style import card_container, custom_success

def show_home():
    """Display the enhanced home page."""
    
    # Main header and introduction
    st.title("Amazon Sentiment Analysis System")
    
    # Hero section with animation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to our advanced sentiment analysis platform!
        
        This application helps businesses understand customer sentiment by analyzing Amazon reviews.
        Leverage the power of Natural Language Processing and AI to gain insights into what your
        customers really think about your products.
        """)
        
        # Call-to-action button
        st.button("Start Analyzing ➡️")
        
    with col2:
        st.image("https://miro.medium.com/v2/1*_JW1JaMpK_fVGld8pd1_JQ.gif", width=250)
    
    # Features section with cards
    st.markdown("## 🌟 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        feature_card("Sentiment Analysis", 
                    "Analyze text data and classify sentiment into Positive, Negative, and Neutral categories.",
                    "📊")
    
    with col2:
        feature_card("Interactive Visualizations", 
                    "Generate insightful charts and visualizations to understand sentiment patterns.",
                    "📈")
    
    with col3:
        feature_card("AI-Powered Summarization", 
                    "Get intelligent summaries of reviews using advanced AI models.",
                    "🤖")
    
    # How it works section
    st.markdown("## 🔍 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        process_step("1️⃣ Import Data", 
                    "Upload your Amazon reviews via Google Sheets or direct file upload.")
    
    with col2:
        process_step("2️⃣ Analyze Sentiment", 
                    "Our NLP model analyzes and categorizes each review.")
    
    with col3:
        process_step("3️⃣ Visualize Results", 
                    "Explore insights through interactive dashboards and reports.")
    
    # Testimonials or use cases
    st.markdown("## 💬 Use Cases")
    
    col1, col2 = st.columns(2)
    
    with col1:
        testimonial_card(
            "Product Development", 
            "Use sentiment analysis to identify product features that customers love or dislike."
        )
    
    with col2:
        testimonial_card(
            "Customer Support", 
            "Detect negative sentiment early to address customer concerns before they escalate."
        )
    
    # Quick stats or interesting facts
    st.markdown("## 📌 Did You Know?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fact_card("90% of consumers read online reviews before making a purchase.")
    
    with col2:
        fact_card("It takes 40 positive reviews to undo the damage of a single negative review.")
    
    with col3:
        fact_card("Reviews with emotional content tend to have a greater impact on purchasing decisions.")
    
    # Call to action footer
    st.markdown("---")
    st.markdown("### Ready to gain insights from your Amazon reviews?")
    st.markdown("Use the sidebar navigation to get started with your analysis!")

def feature_card(title, description, emoji):
    """Display a feature card with an emoji, title, and description."""
    st.markdown(f"""
    <div style="padding: 15px; background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); height: 200px;">
        <div style="font-size: 40px; text-align: center; margin-bottom: 10px;">{emoji}</div>
        <h3 style="text-align: center; color: #2c3e50;">{title}</h3>
        <p style="text-align: center; color: #34495e;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def process_step(title, description):
    """Display a process step card."""
    st.markdown(f"""
    <div style="padding: 15px; background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px;">
        <h3 style="color: #3498db;">{title}</h3>
        <p style="color: #34495e;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def testimonial_card(title, text):
    """Display a testimonial or use case card."""
    st.markdown(f"""
    <div style="padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px; margin-bottom: 15px;">
        <h4 style="color: #2c3e50;">{title}</h4>
        <p style="color: #34495e; font-style: italic;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

def fact_card(fact):
    """Display an interesting fact card."""
    st.markdown(f"""
    <div style="padding: 15px; background-color: #e8f4fc; border-radius: 8px; text-align: center; height: 120px; display: flex; align-items: center; justify-content: center;">
        <p style="color: #2980b9; font-weight: 500; margin: 0;">{fact}</p>
    </div>
    """, unsafe_allow_html=True)