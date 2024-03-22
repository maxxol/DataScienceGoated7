# sentiment_analysis.py

import numpy as np
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from textblob import TextBlob
import math
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute path to twitterdata.csv
csv_path = os.path.join(current_dir, 'twitterdata.csv')
def analyze_sentiment(datafilterkeyword: str):
    # Importing the dataset and setting up pandas
    pd.set_option('display.max_colwidth', 255)
    DATASET_COLUMNS = ['target', 'id', 'date', 'flag', 'user', 'twitter message']
    DATASET_ENCODING = "ISO-8859-1"
    df = pd.read_csv(csv_path, encoding=DATASET_ENCODING, names=DATASET_COLUMNS)
    del df['target']  # delete unused column
    del df['user']  # delete unused column
    del df['date']  # delete unused column
    del df['flag']  # delete unused column

    filtered_data = df[df['twitter message'].str.contains(datafilterkeyword)]  # filter data

    class Mood:
        sentiment: float

        def __init__(self, sentiment: float):
            self.sentiment = sentiment

    def bubbleSort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

    def get_mood(input_text: str, *, threshold: float, totalpositive: int, totalneutral: int, totalnegative: int) -> tuple[
        Mood, int, int, int]:
        sentiment: float = TextBlob(input_text).sentiment.polarity

        if sentiment >= threshold:
            mood = Mood(sentiment)
            totalpositive += 1
        elif sentiment <= -threshold:
            mood = Mood(sentiment)
            totalnegative += 1
        else:
            mood = Mood(sentiment)
            totalneutral += 1

        return mood, totalpositive, totalneutral, totalnegative

    # Initiating variables
    resultMood = ''
    totalsentiment = 0
    totalsentimentvalues = 0
    averagesentiment = 0
    mediansentiment = 0
    sentimentarray = []
    totalpositive = 0
    totalneutral = 0
    totalnegative = 0
    standarddeviation = 0
    threshold = 0.15

    for index, row in filtered_data.iterrows():
        text: str = row['twitter message']
        mood, totalpositive, totalneutral, totalnegative = get_mood(text, threshold=threshold,
                                                                    totalpositive=totalpositive,
                                                                    totalneutral=totalneutral,
                                                                    totalnegative=totalnegative)

        totalsentiment += mood.sentiment
        totalsentimentvalues += 1
        sentimentarray.append(mood.sentiment)

    bubbleSort(sentimentarray)

    mediansentiment = round(sentimentarray[math.floor(len(sentimentarray) / 2)], 3)
    averagesentiment = round(totalsentiment / totalsentimentvalues, 3)
    standarddeviation = round(np.std(sentimentarray), 3)
    if averagesentiment >= threshold:
        resultMood = ':D'
    elif averagesentiment <= -threshold:
        resultMood = '>:('
    else:
        resultMood = ':|'

    print("--- sentiment for '" + datafilterkeyword + "'---\naverage sentiment value:", averagesentiment, resultMood,
          "\nmedian sentiment:", mediansentiment, "\nstandard deviation:", standarddeviation,
          "\n# pos/neu/neg:", totalpositive, "/", totalneutral, "/", totalnegative)

    # Unify Text from all weeks
    text = filtered_data['twitter message'].str.cat(sep=' ')

    # Set the stopwords list
    stopwords = set(STOPWORDS)
    new_words = ["feel", "feeling"]
    new_stopwords = stopwords.union(new_words)

    # Size of Word Cloud
    plt.rcParams["figure.figsize"] = (7, 4)

    # Make Wordcloud
    wordcloud = WordCloud(max_font_size=50, max_words=80, background_color="white", stopwords=new_stopwords,
                          colormap='jet').generate(text)

    # Plot Wordcloud
    plt.plot()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

# Call the function with the desired datafilterkeyword
if __name__ == '__main__':
    analyze_sentiment("birthday")
