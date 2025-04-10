import tweepy
from pymongo import MongoClient
from textblob import TextBlob
from collections import Counter

# Twitter API setup
bearer_token = "AAAAAAAAAAAAAAAAAAAAADggzgEAAAAA6JiawBCNo4da7fpF2dVkz8N18hE%3DijCTjPCrMHHbL6QMo4ZUZHsLni2K8bHfrEt7vp0rERE75fOLfI"
client = tweepy.Client(bearer_token=bearer_token)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["twitter_db"]
tweets_collection = db["tweets"]
users_collection = db["users"]

# Fetch and store tweets with sentiment
try:
    tweets = client.search_recent_tweets(
        query="#python",
        max_results=10,
        tweet_fields=["author_id", "created_at"]
    )
    
    if tweets.data:
        for tweet in tweets.data:
            analysis = TextBlob(tweet.text)
            polarity = analysis.sentiment.polarity
            sentiment = "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"
            
            tweet_data = {
                "tweet_id": str(tweet.id),
                "text": tweet.text,
                "username": str(tweet.author_id),
                "created_at": str(tweet.created_at),
                "sentiment": sentiment
            }

            tweets_collection.insert_one(tweet_data)
            print(f"Saved: {tweet.text} | Sentiment: {sentiment}")

            username = str(tweet.author_id)
            update_fields = {"$inc": {"tweet_count": 1}}
            if sentiment == "positive":
                update_fields["$inc"]["positive_count"] = 1
            elif sentiment == "negative":
                update_fields["$inc"]["negative_count"] = 1
            else:
                update_fields["$inc"]["neutral_count"] = 1

            users_collection.update_one(
                {"username": username},
                update_fields,
                upsert=True
            )
    else:
        print("❗ No tweets returned from Twitter API.")
except tweepy.TooManyRequests:
    print("🚫 Rate limit reached! Try again later.")
except tweepy.BadRequest as e:
    print(f"🚫 Bad Request Error: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
