import streamlit as st
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['social_media_data']

# Function to fetch data from MongoDB and convert to DataFrame
def fetch_data(collection_name, limit=100, db=None):
    collection = db[collection_name]
    data = collection.find().limit(limit)
    df = pd.DataFrame(list(data))
    return df

# Title of the application
st.title("Engagement Predictor Using Linear Regression")

# Fetch data from MongoDB
df_posts = fetch_data('Instagram_Posts', db=db)

# Display the data
st.subheader("Instagram Posts Data")
st.dataframe(df_posts.head(10))

# Select features and target
st.write("Select Features and Target")
all_columns = df_posts.columns.tolist()

# Filter only numeric columns because Linear Regression only allows numeric types
numeric_columns = df_posts.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Display feature selection with numeric columns only
features = st.multiselect("Select Features", numeric_columns, default=['num_comments', 'likes', 'video_view_count', 'video_play_count'])
target = 'engagement_score_view'  # Set the target to engagement_score_view

# Handle missing values
missing_value_option = st.radio("How do you want to handle missing values?", ('Drop rows with missing values', 'Fill missing values with mean'))

if len(features) > 0 and target:
    # Prepare the data
    X = df_posts[features]
    y = df_posts[target]

    # Handle missing values
    if missing_value_option == 'Drop rows with missing values':
        X = X.dropna()
        y = y.loc[X.index]  # Ensure target matches the dropped feature indices
    else:
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Display evaluation metrics
    st.write(f"Mean Squared Error: {mse}")
    st.write(f"R^2 Score: {r2}")

    # Display the equation of the linear regression
    st.write("Linear Regression Equation:")
    intercept = model.intercept_
    st.write(f"Intercept: {intercept}")
 
     # Visualize the results
    st.subheader("Actual vs Predicted")
    
    # Separate line charts for Actual and Predicted values
    st.line_chart(y_test.rename("Actual"), use_container_width=True, color='#FF5733')
    st.line_chart(pd.Series(y_pred, index=y_test.index).rename("Predicted"), use_container_width=True, color='#33FF68')

else:
    st.write("Please select at least one feature and a target.")

# Project benefits and explanations
st.markdown("## How Can This Help With The Project? ")
st.markdown("1. This dataset (Instagram Posts) already contains an engagement score view but the others do not. Can estimate prediction values for the other, and allow users to compare predicted engagement values across different social media platforms.")
st.markdown("2. The dropdown feature selection allows for testing different target values to identify which ones produce the most accurate engagement predictions.")
