# -*- coding: utf-8 -*-
"""Program Analisis Sentimen Apk Kredivo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KaW5CM6WMXpuCi3B4BqpZ319BeiT5mpX

**Program Analisis Sentimen Apk Kredivo**
"""

!pip install google-play-scraper
from google_play_scraper import Sort, reviews
result, continuation_token = reviews(
'com.finaccel.android',
lang='id',
country='id',
sort=Sort.MOST_RELEVANT,
count=10000, # defaults to 100
filter_score_with=None
)

import string
import nltk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""**Membuat Data Frame**"""

data = pd.DataFrame(np.array(result), columns=['review'])
data = data.join(pd.DataFrame(data.pop('review').tolist()))
scrappeddata1 = data[['content','score','at']]
sorteddata = scrappeddata1.sort_values(by='at', ascending=True) #Sort by Newest, change to True if you want to sort by Oldest.
sorteddata.head()

"""Download Data"""

sorteddata.to_csv("review_kredivo.csv", index = False)

"""**Menambahkan Kolom Year, Month dan Day dari kolom at**"""

sorteddata['Year'] = sorteddata['at'].dt.year
sorteddata['Month'] = sorteddata['at'].dt.month
sorteddata['Day'] = sorteddata['at'].dt.day
sorteddata

"""**Menghapus kolom at**"""

df = sorteddata[['content','score','Year','Month','Day']]
df

"""**Menghitung Rekapitulasi Score**"""

df['score'].value_counts()

"""**Visualisasi Review Berdasarkan Score**"""

import seaborn as sns
result = df.groupby(['score']).size()
# plot the result
sns.barplot(x = result.index, y = result.values)

"""**Kolom Sentimen**"""

sentimen = []
for index, row in df.iterrows():
  if row['score'] > 3 :
    sentimen.append(1)
  else:
    sentimen.append(-1)
df['sentiment'] = sentimen
df.head()

"""**Distribusi Sentimen**"""

df_new = df[['Year', 'Month', 'sentiment']]
result = df_new.groupby(['sentiment']).size()
# plot the result
sns.barplot(x = result.index, y = result.values)

"""**Visualisasi Sentiment dalam bentuk Piechart**"""

#pie chart to show percentage distribution of polarity
from matplotlib import pyplot as plt
fig = plt.figure(figsize=(7,7))
colors = ('green', 'red')
wp={'linewidth':2, 'edgecolor': 'black'}
tags=df_new['sentiment'].value_counts()
explode = (0.1,0.1)
tags.plot(kind='pie', autopct='%1.1f%%', shadow=True, colors=colors,
startangle=90, wedgeprops=wp, explode=explode, label='')
plt.title('Distribution of sentiment')

"""**Distribusi Sentiment per Tahun**"""

df3 = df_new.groupby(['Year','sentiment'])['sentiment'].count()
df3

"""**TEXT Pre-PROCESSING**

**DATA CLEANING**

Data Description
"""

sorteddata.info()

"""Berdasarkan output diatas, dapat disimpulkan bahwa dataset tersebut, memiliki total: 3 kolom, dengan jumlah maksimal baris untuk setiap kolom sebanyak: 10000 baris

Detecting the Missing Value
"""

sorteddata.isnull()

sorteddata.isnull().any()

"""Berdasarkan output diatas, jika hasil output tertulis False, hal tersebut memberikan arti bahwa kolom tersebut tidak mengandung Missing Values

CASE FOLDING
"""

df['content'] = df['content'].str.replace('https\S+', ' ', case=False)
df['content'] = df['content'].str.lower()
df['content'] = df['content'].str.replace('@\S+', ' ', case=False)
df['content'] = df['content'].str.replace('#\S+', ' ', case=False)
df['content'] = df['content'].str.replace("\'\w+", ' ', case=False)
df['content'] = df['content'].str.replace("[^\w\s]", ' ', case=False)
df['content'] = df['content'].str.replace("\s(2)", ' ', case=False)

# impor word_tokenize dari modul nltk
from nltk.tokenize import word_tokenize
#df['content']=df.apply(lambda row: nltk.word_tokenize(row['content']), axis=1)
from nltk.tokenize import RegexpTokenizer
tk = RegexpTokenizer('\w+')
df['content_token']=df['content'].apply(tk.tokenize)
df.head(3)

"""Filtering (Stopword Removal)"""

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
# Make a list of Indonesian stopwords
stopwords = nltk.corpus.stopwords.words("indonesian")
# Extend the list with your own custom stopwords
my_stopwords = ['kredivo']
stopwords.extend(my_stopwords)
# Remove stopwords
df['content_token'] = df['content_token'].apply(lambda x: [item for item in x if item not in stopwords])
df.head(3)

"""**Stemming sastrawi**"""

!pip install Sastrawi
# import Sastrawi package
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()
df['stemmed'] = df['content_token'].apply(lambda x: [stemmer.stem(y) for y in x]) # Stem every word.
df.head(5)

"""Menghapus token yang kurang dari 4 karakter"""

df['text_string'] = df['stemmed'].apply(lambda x: ' '.join([item for item in x if len(item)>3]))
df.head(5)

"""Merubah tipe kolom text_string dari object menjadi string"""

df['text_string'] = df['text_string'].astype('str')
df['text_string'] = df['text_string'].astype(pd.StringDtype())
df.dtypes

df.head()
df.to_csv("review_kredivo_stemming.csv", index = False)

df.to_csv("review_kredivo_stemming.txt", index = False)

"""WORDCLOUD"""

!pip install wordcloud

"""Wordcloud Sentiment Positif"""

# Commented out IPython magic to ensure Python compatibility.
df_p=df[df['sentiment']==1]
all_words_lem = ' '.join([word for word in df_p['text_string']])
# %matplotlib inline
import matplotlib.pyplot as plt
from wordcloud import WordCloud
wordcloud = WordCloud(background_color='white', width=800, height=500, random_state=21, max_font_size=130).generate(all_words_lem)
plt.figure(figsize=(20, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off');

"""Wordcloud Sentiment Negatif"""

# Commented out IPython magic to ensure Python compatibility.
df_neg=df[df['sentiment']==-1]
all_words_lemneg = ' '.join([word for word in df_neg['text_string']])
# %matplotlib inline
import matplotlib.pyplot as plt
from wordcloud import WordCloud
wordcloud = WordCloud(background_color='white', width=800, height=500, random_state=21, max_font_size=130).generate(all_words_lemneg)
plt.figure(figsize=(20, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off');

"""Sentiment Analysis Menggunakan SVM"""

# Commented out IPython magic to ensure Python compatibility.
# Text Preprocessing & Cleaning
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import re
from wordcloud import WordCloud,STOPWORDS
from nltk import SnowballStemmer
from sklearn.model_selection import train_test_split # Split Data
from imblearn.over_sampling import SMOTE # Handling Imbalanced
# Model Building

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report , confusion_matrix , accuracy_score # Performance Metrics
# Data Visualization
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
# %matplotlib inline

# split x dan y
x = df['text_string']
y = df['sentiment']

"""Menerapkan TF-IDF"""

tfid = TfidfVectorizer()
X_final =  tfid.fit_transform(x)

"""Handling Imbalance"""

# Handling imbalanced using SMOTE
smote = SMOTE()
x_sm,y_sm = smote.fit_resample(X_final,y)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2) #atur data testing

x_test

# perform count vectorizer
vectorizer = CountVectorizer()
vectorizer.fit(x_train)

# x_train
x_train = vectorizer.transform(x_train)
x_test = vectorizer.transform(x_test)

x_train.toarray()

for c in [0.01, 0.05, 0.25, 0.5, 0.75, 1]:
  svm = LinearSVC(C=c)
  svm.fit(x_train, y_train)
  print('Akurasi untuk c = %s: %s' %(c, accuracy_score(y_test, svm.predict(x_test))))

svm = LinearSVC(C=0.05)
svm.fit(x_train, y_train)

print('Akurasi score model final: %s: %s' %(c, accuracy_score(y_test, svm.predict(x_test))))

"""**Evaluasi Model**"""

y_pred = svm.predict(x_test)
print('Accuracy of SVM classifier on test set : {:.4f}'.format(svm.score(x_test, y_test)))

confusion_matrix = confusion_matrix(y_test, y_pred)
print(confusion_matrix)
print(classification_report(y_test, y_pred))