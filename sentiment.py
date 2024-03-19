# utilities
import numpy as np
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
#sentiment analysis
from textblob import TextBlob
import math



# Importing the dataset and setting up pandas
pd.set_option('display.max_colwidth', 255)
DATASET_COLUMNS=['target','id','date','flag','user','twitter message']
DATASET_ENCODING = "ISO-8859-1"
df = pd.read_csv('twitterdata.csv', encoding=DATASET_ENCODING, names=DATASET_COLUMNS)
del df['target'] #delete unused collumn
del df['user'] #delete unused collumn
del df['date'] #delete unused collumn
del df['flag'] #delete unused collumn

datafilterkeyword = " birthday " #keyword by which to filter data
filtered_data = df[df['twitter message'].str.contains(datafilterkeyword)] #filter data


class Mood: #class for the sentiment
    sentiment: float

    def __init__(self, sentiment: float):
        self.sentiment = sentiment

# Python3 program for Bubble Sort Algorithm Implementation source: https://www.geeksforgeeks.org/sorting-algorithms-in-python/
def bubbleSort(arr):
     
    n = len(arr)
 
    # For loop to traverse through all 
    # element in an array
    for i in range(n):
        for j in range(0, n - i - 1):
             
            # Range of the array is from 0 to n-i-1
            # Swap the elements if the element found 
            #is greater than the adjacent element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                 



def get_mood(input_text: str, *, threshold: float, totalpositive: int, totalneutral: int, totalnegative: int) -> tuple[Mood, int, int, int]: #sentiment generator
    sentiment: float = TextBlob(input_text).sentiment.polarity #generate the sentiment

    if sentiment >= threshold: #catagorize the sentiment to positive, negative and neutral
        mood = Mood(sentiment)
        totalpositive += 1
    elif sentiment <= -threshold:
        mood = Mood(sentiment)
        totalnegative += 1
    else:
        mood = Mood(sentiment)
        totalneutral += 1

    return mood, totalpositive, totalneutral, totalnegative


if __name__ == '__main__':
    #initiating variables
    resultMood = ''
    totalsentiment = 0 #all sentiment added up
    totalsentimentvalues= 0 #number of collected sentiment values
    averagesentiment = 0 #total/collected
    mediansentiment = 0 #the median
    sentimentarray = [] #array with every collected value
    totalpositive = 0 #positive values
    totalneutral = 0 #neutral values
    totalnegative = 0 #negative values
    standarddeviation = 0 #standard deviation
    threshold=0.15
    

for index, row in filtered_data.iterrows(): #for every row in the filtered data table
    text: str = row['twitter message'] #set the input text to the indexed twitter message
    mood, totalpositive, totalneutral, totalnegative = get_mood(text, threshold=threshold, totalpositive=totalpositive, totalneutral=totalneutral, totalnegative=totalnegative) #generate the sentiment values

    totalsentiment += mood.sentiment
    totalsentimentvalues += 1
    sentimentarray.append(mood.sentiment)


bubbleSort(sentimentarray) #sort the sentimentarray to get median

mediansentiment = round(sentimentarray[math.floor(len(sentimentarray)/2)],3)
averagesentiment = round(totalsentiment/totalsentimentvalues,3)
standarddeviation = round(np.std(sentimentarray),3)
if averagesentiment >= threshold: #catagorize the sentiment to positive, negative and neutral
    resultMood = ':D'
elif averagesentiment <= -threshold:
    resultMood = '>:('
else:
    resultMood = ':|'

print("--- sentiment for '" + datafilterkeyword + "'---\naverage sentiment value:",averagesentiment,resultMood,"\nmedian sentiment:",mediansentiment,"\nstandard deviation:",standarddeviation,"\n# pos/neu/neg:",totalpositive,"/",totalneutral,"/",totalnegative)


# Unify Text from all weeks
text = filtered_data['twitter message'].str.cat(sep=' ')
     

#set the stopwords list
stopwords= set(STOPWORDS)
new_words = ["feel", "feeling"]
new_stopwords=stopwords.union(new_words)
     

# Size of Word Cloud
plt.rcParams["figure.figsize"] = (7,4)

# Make Wordcloud
wordcloud = WordCloud(max_font_size=50, max_words=80, background_color="white",stopwords=new_stopwords, colormap='jet').generate(text)

# Plot Wordcloud
plt.plot()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()