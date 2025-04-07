import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK resources (only needs to run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def suggest_tag(text):
    """
    Suggest a business-oriented tag based on review content.
    Returns a tag like "Late Delivery", "Excellent Customer Support", etc.
    """
    text = str(text).lower()
    
    # Dictionary of keywords for each category
    tag_keywords = {
        "Late Delivery": [
            "late", "delay", "slow", "shipping", "delivery", "arrive", "wait", 
            "weeks", "days", "long time", "never arrived", "tracking"
        ],
        "Excellent Customer Support": [
            "support", "service", "helpful", "responsive", "customer service", 
            "representative", "agent", "solved", "resolution", "prompt response"
        ],
        "Defective Product": [
            "defect", "broken", "damage", "malfunction", "not working", "faulty",
            "quality issue", "didn't work", "doesn't work", "stopped working"
        ],
        "Value for Money": [
            "worth", "price", "value", "cheap", "expensive", "cost", "bargain",
            "overpriced", "affordable", "good deal", "not worth"
        ],
        "Product Quality": [
            "quality", "durable", "well made", "material", "sturdy", "solid",
            "construction", "premium", "build quality", "craftsmanship"
        ],
        "Packaging Issues": [
            "package", "packaging", "box", "wrap", "sealed", "container",
            "damaged box", "torn", "crushed", "poorly packed"
        ],
        "Feature Satisfaction": [
            "feature", "functionality", "works well", "user friendly", "convenient",
            "easy to use", "intuitive", "difficult to use", "complicated"
        ],
        "Size or Fit Issues": [
            "size", "fit", "small", "large", "tight", "loose", "measurement",
            "dimension", "bigger", "smaller", "too big", "too small"
        ],
        "Return/Refund Experience": [
            "return", "refund", "money back", "exchange", "policy", "warranty",
            "replacement", "sent back", "customer service", "return process"
        ],
        "Recommendation": [
            "recommend", "suggestion", "advise", "worth buying", "wouldn't recommend",
            "highly recommend", "suggest", "tell friends", "buy again"
        ]
    }
    
    # Count keyword matches for each category
    tag_scores = {tag: 0 for tag in tag_keywords}
    
    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            if keyword in text:
                tag_scores[tag] += 1
    
    # Find tag with the highest score
    max_score = max(tag_scores.values())
    if max_score == 0:
        return "General Comment"  # Default when no specific tag matches
    
    # Get the tag with highest score
    best_tags = [tag for tag, score in tag_scores.items() if score == max_score]
    return best_tags[0]  # Return the first tag with highest score

def analyze_dataframe_tags(df, column_name):
    """
    Add tags to a dataframe based on text content in specified column.
    Returns: The dataframe with an added 'Tag' column
    """
    result_df = df.copy()
    result_df['Tag'] = result_df[column_name].apply(suggest_tag)
    return result_df