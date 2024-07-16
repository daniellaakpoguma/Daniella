import streamlit as st
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download NLTK resources if not already downloaded
nltk.download('stopwords')
nltk.download('punkt')

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['social_media_data']

# Function to fetch comments and descriptions with hashtags from MongoDB
def fetch_data(collection_name, limit=100, db=None):
    collection = db[collection_name]
    data = collection.find().limit(limit)
    if collection_name == 'Instagram_Comments':
        text_data = [comment['comment'] for comment in data]
        hashtags_data = [comment['hashtags'] if 'hashtags' in comment else '' for comment in data]
    elif collection_name == 'Tiktok_Posts':
        text_data = [post['description'] for post in data]
        hashtags_data = [post['hashtags'] if 'hashtags' in post else '' for post in data]
    else:
        raise ValueError(f"Collection name '{collection_name}' not recognized.")
    return text_data, hashtags_data

# Function for text preprocessing
def preprocess_text(text):
    if isinstance(text, str):
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())  # Tokenize and lowercase
        filtered_text = [word for word in word_tokens if word.isalnum() and word not in stop_words]  # Remove stopwords and non-alphanumeric tokens
        return ' '.join(filtered_text)
    else:
        return ""  # Return empty string or handle differently based on your needs


# Fetch comments and descriptions with hashtags from MongoDB
comments, hashtags = fetch_data('Instagram_Comments', db=db)
tiktok_descriptions, tiktok_hashtags = fetch_data('Tiktok_Posts', db=db)

# Clean and preprocess data
cleaned_comments = [preprocess_text(comment) for comment in comments]
cleaned_descriptions = [preprocess_text(description) for description in tiktok_descriptions]
cleaned_hashtags = [preprocess_text(hashtag) for hashtag in hashtags + tiktok_hashtags]  # Combine and preprocess hashtags

# Combine cleaned comments and descriptions for topic modeling
all_texts = cleaned_comments + cleaned_descriptions

# Assuming 'all_texts' is a list of preprocessed texts
vectorizer = TfidfVectorizer(max_features=1000, max_df=0.95, min_df=2)
tfidf_matrix = vectorizer.fit_transform(all_texts)

# Create an LDA model
lda_model = LatentDirichletAllocation(n_components=5, random_state=42)  # Adjust n_components as needed
lda_output = lda_model.fit_transform(tfidf_matrix)

# Function to display topics
def display_topics(model, feature_names, no_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        topic_words = [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]
        topics.append({
            "Topic": topic_idx + 1,
            "Top Words": ", ".join(topic_words)
        })
    return topics

# Streamlit UI
st.title("Social Media Topic Modeling")

# Display topics found by LDA for Instagram Comments
st.subheader("Topics in Instagram Comments")
feature_names = vectorizer.get_feature_names_out()
topics_instagram = display_topics(lda_model, feature_names, 10)
for topic in topics_instagram:
    st.write(f"**Topic {topic['Topic']}**")
    st.write(topic['Top Words'])
    st.write("---")

# Display topics found by LDA for TikTok Post Descriptions
st.subheader("Topics in TikTok Post Descriptions")
topics_tiktok = display_topics(lda_model, feature_names, 10)
for topic in topics_tiktok:
    st.write(f"**Topic {topic['Topic']}**")
    st.write(topic['Top Words'])
    st.write("---")

# Optional: Display topics found by LDA for Hashtags
st.subheader("Topics in TikTok Post Hashtags")
topics_hashtags = display_topics(lda_model, feature_names, 10)
for topic in topics_hashtags:
    st.write(f"**Topic {topic['Topic']}**")
    st.write(topic['Top Words'])
    st.write("---")
