from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["twitter_db"]
collection = db["tweets"]

# Check what’s already stored
stored_tweets = collection.find()
print("\nStored Tweets:")
for tweet in stored_tweets:
    print(tweet["text"])