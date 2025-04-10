import streamlit as st

def apply_custom_style():
    """Apply custom styling to the Streamlit app."""
    
    # Add custom CSS
    st.markdown("""
    <style>
        /* Main container */
        .main {
            background-color: #f8f9fa;
            padding: 20px;
        }
        
        /* Headers */
        h1 {
            color: #2c3e50;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        
        h2, h3 {
            color: #34495e;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 600;
            margin-top: 20px;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #2c3e50;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Cards for content sections */
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Improve dataframe appearance */
        .dataframe {
            border-collapse: collapse;
            border: none;
            font-size: 14px;
        }
        
        .dataframe th {
            background-color: #3498db;
            color: white;
            font-weight: 500;
            padding: 8px;
        }
        
        .dataframe td {
            padding: 8px;
            border-bottom: 1px solid #eaeaea;
        }
        
        /* Success/warning/error messages */
        .success {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #28a745;
            margin: 10px 0;
        }
        
        .warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }
        
        .error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #dc3545;
            margin: 10px 0;
        }
        
        /* Custom progress bar */
        .stProgress > div > div {
            background-color: #3498db;
        }
    </style>
    """, unsafe_allow_html=True)

def card_container(content_function):
    """Decorator to wrap content in a card container."""
    def wrapper(*args, **kwargs):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        content_function(*args, **kwargs)
        st.markdown('</div>', unsafe_allow_html=True)
    return wrapper

def custom_success(text):
    """Display a custom success message."""
    st.markdown(f'<div class="success">{text}</div>', unsafe_allow_html=True)

def custom_warning(text):
    """Display a custom warning message."""
    st.markdown(f'<div class="warning">{text}</div>', unsafe_allow_html=True)

def custom_error(text):
    """Display a custom error message."""
    st.markdown(f'<div class="error">{text}</div>', unsafe_allow_html=True)