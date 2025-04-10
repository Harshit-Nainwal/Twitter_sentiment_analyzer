from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
import tweepy
from textblob import TextBlob

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your own secret key!

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['twitterAnalyzer']
users_collection = db['users']
tweets_collection = db['tweets']

# Tweepy setup
bearer_token = "AAAAAAAAAAAAAAAAAAAAADggzgEAAAAA6JiawBCNo4da7fpF2dVkz8N18hE%3DijCTjPCrMHHbL6QMo4ZUZHsLni2K8bHfrEt7vp0rERE75fOLfI"  # Replace this with your token
twitter_client = tweepy.Client(bearer_token=bearer_token)

# Sentiment analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"

# Home redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = {
            "name": request.form['name'],
            "email": request.form['email'],
            "contact": request.form['contact'],
            "gender": request.form['gender'],
            "age": request.form['age']
        }
        user_id = users_collection.insert_one(user).inserted_id
        session['user_id'] = str(user_id)
        session['username'] = user['name']
        return redirect(url_for('analyze'))
    return render_template('login.html')

# Tweet Analysis UI (After login)
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        option = request.form.get("option")

        if option == "random":
            try:
                tweets = twitter_client.search_recent_tweets(query="#python", max_results=10, tweet_fields=["author_id", "created_at"])
                tweet_list = []

                for tweet in tweets.data:
                    sentiment = analyze_sentiment(tweet.text)
                    tweet_data = {
                        "tweet_id": str(tweet.id),
                        "text": tweet.text,
                        "username": str(tweet.author_id),
                        "created_at": str(tweet.created_at),
                        "sentiment": sentiment
                    }
                    tweets_collection.insert_one(tweet_data)
                    tweet_list.append(tweet_data)
                return render_template("results.html", tweets=tweet_list, mode="random")

            except Exception as e:
                return render_template("results.html", error=str(e))

        elif option == "specific":
            username = request.form.get("username")
            try:
                user = twitter_client.get_user(username=username)
                user_id = user.data.id
                tweets = twitter_client.get_users_tweets(id=user_id, max_results=5, tweet_fields=["created_at"])

                if not tweets.data:
                    return render_template("results.html", error="No tweets found")

                tweet = tweets.data[0]
                sentiment = analyze_sentiment(tweet.text)
                tweet_data = {
                    "tweet_id": str(tweet.id),
                    "text": tweet.text,
                    "username": username,
                    "created_at": str(tweet.created_at),
                    "sentiment": sentiment
                }
                tweets_collection.insert_one(tweet_data)
                return render_template("results.html", tweets=[tweet_data], mode="specific", twitter_username=username)

            except Exception as e:
                return render_template("results.html", error=str(e))

    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
