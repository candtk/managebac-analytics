from textblob import TextBlob
import re


def clean_message(message):
    """
    Strips URLs, mentions, and special characters from a message
    using regex before passing it to sentiment analysis.
    """
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", message).split())


def get_message_sentiment(message):
    """
    Classifies the sentiment of a message as positive, neutral, or negative
    using TextBlob's sentiment polarity score.
    """
    analysis = TextBlob(clean_message(message))
    if analysis.sentiment.polarity > 0:
        return 'positive', analysis.sentiment.polarity
    elif analysis.sentiment.polarity == 0:
        return 'neutral', analysis.sentiment.polarity
    else:
        return 'negative', analysis.sentiment.polarity


def sentiment_analysis(message):
    cleanedmessage = clean_message(message)
    return get_message_sentiment(cleanedmessage)
