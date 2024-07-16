import streamlit as st

# Title
st.title("Social Media Dashboard")

platforms = ["Facebook", "Pinterest", "TikTok", "YouTube", "Instagram"]  # List of platforms

# Grid Layout
row1 = st.columns(3)  # First row with 3 columns
row2 = st.columns(2)  # Second row with 2 columns

# Display platform boxes in row1
for i, col in enumerate(row1):
    with col:
        tile = st.container(height=120)
        tile.subheader(platforms[i])
        tile.button(f"See General Metrics", key=f"button_{platforms[i]}")

# Display platform boxes in row2
for i, col in enumerate(row2):
    with col:
        tile = st.container(height=120)
        tile.subheader(platforms[len(row1) + i])
        tile.button(f"See General Metrics", key=f"button_{platforms[len(row1) + i]}")

#General Metrics Container
general_metrics = st.container()
with general_metrics:
    st.write("General Engagement Metrics:")
    st.markdown("""
    Metrics to Display:
    - **Average Engagement Rate:** Average likes, comments, shares, retweets per post/comment/page
    - **Demographics:** Breakdown of audience demographics (age group) - using best social media dataset
    - **Content Type Performance:** Engagement rates for different types of content (videos, images, text).
    - **Hashtag Performance:** Effectiveness of hashtags used.
    """)
 
option = st.selectbox(
   "What would you like to focus on today?",
   ("Best Time to Post", "Video Duration Performance", "Content Type Preference", "Hashtag Effectiveness", "Audience Demographics", "Engagement Trends"),
   index=None,
   placeholder="Select contact method...",
)



