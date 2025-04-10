import tweepy
from pymongo import MongoClient
from textblob import TextBlob

# Twitter API setup
bearer_token = "AAAAAAAAAAAAAAAAAAAAADggzgEAAAAA6JiawBCNo4da7fpF2dVkz8N18hE%3DijCTjPCrMHHbL6QMo4ZUZHsLni2K8bHfrEt7vp0rERE75fOLfI"  # Replace with your token
client = tweepy.Client(bearer_token=bearer_token)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["twitter_db"]
tweets_collection = db["tweets"]

# Function to analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return "positive" if analysis.sentiment.polarity > 0 else "negative" if analysis.sentiment.polarity < 0 else "neutral"

# Get Twitter username from user input
twitter_username = input("Enter the Twitter username (e.g., elonmusk) to analyze their recent tweet: ")

try:
    # Get user by username
    user = client.get_user(username=twitter_username)
    if not user.data:
        print(f"User '{twitter_username}' not found.")
    else:
        user_id = user.data.id
        print(f"Found user: {twitter_username} (ID: {user_id})")

        # Fetch the user's most recent tweet
        tweets = client.get_users_tweets(id=user_id, max_results=5, 
                                         tweet_fields=["created_at"])
        if not tweets.data:
            print(f"No recent tweets found for {twitter_username}.")
        else:
            # Take the most recent tweet (first in list)
            recent_tweet = tweets.data[0]
            text = recent_tweet.text
            sentiment = analyze_sentiment(text)

            # Store in MongoDB
            tweet_data = {
                "tweet_id": str(recent_tweet.id),
                "text": text,
                "username": str(user_id),
                "created_at": str(recent_tweet.created_at),
                "sentiment": sentiment
            }
            tweets_collection.insert_one(tweet_data)

            # Show result
            print("\nRecent Tweet Analysis:")
            print(f"Text: {text}")
            print(f"Username: {twitter_username} (ID: {user_id})")
            print(f"Created At: {recent_tweet.created_at}")
            print(f"Sentiment: {sentiment}")
            print("Tweet saved to MongoDB.")

except tweepy.TooManyRequests:
    print("Rate limit reached! Wait 15 minutes or check monthly quota.")
except tweepy.BadRequest as e:
    print(f"Bad Request Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")