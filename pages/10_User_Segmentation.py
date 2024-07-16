import streamlit as st
from pymongo import MongoClient
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt


# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['social_media_data']

# Function to fetch data from MongoDB and convert to DataFrame
def fetch_data(collection_name, limit=100, db=None):
    collection = db[collection_name]
    data = collection.find().limit(limit)
    df = pd.DataFrame(list(data))
    return df

# Fetch data from MongoDB
df_posts = fetch_data('Tiktok_Posts', db=db)

# Title of the application
st.title("User Segmentation")

st.write("## Using Profiles")
st.write("Most datasets have information like content type, page category.")
st.write("For Instagram: if it's a business or personal account so further machine learning does not need to be carried out on for Social Media Profiles.")
st.write("Also profiles, TikTok has engagement metrics for each profile, region or NLP which highest engagements.")


st.write("## Using Posts")
st.write("Segment posts based on their level of engagement.")
st.write("E.g Which Length of Videos have higher engagament")
# Select relevant columns for clustering
X = df_posts[['share_count', 'play_count', 'video_duration', 'comment_count']]

# Impute missing values
imputer = SimpleImputer(strategy='mean')  # You can also use 'median', 'most_frequent', etc.
X_imputed = imputer.fit_transform(X)

# Standardize the data (important for K-means)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# Apply K-means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
df_posts['cluster'] = kmeans.fit_predict(X_scaled)

# Analyze clusters
cluster_analysis = df_posts.groupby('cluster').agg({
    'share_count': 'mean',
    'play_count': 'mean',
    'video_duration': 'mean',
    'comment_count': 'mean'
}).reset_index()

# Display cluster characteristics
st.subheader("Cluster Analysis")
st.write(cluster_analysis)

# Optional: Visualize insights (e.g., histograms, charts)
st.subheader("Visualize Insights")
# Example: Display distribution of video durations per cluster
for cluster in cluster_analysis['cluster']:
    st.write(f"Cluster {cluster} - Video Duration Distribution")
    fig, ax = plt.subplots()
    df_posts[df_posts['cluster'] == cluster]['video_duration'].hist(ax=ax, bins=20)
    ax.set_title(f"Cluster {cluster} - Video Duration Distribution")
    ax.set_xlabel("Video Duration")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

