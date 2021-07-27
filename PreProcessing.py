import pandas as pd
from textblob import TextBlob
import string, re
from flask import *
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import swifter
import pickle

def cleansing(data):
        # lower text
        data = data.lower()

        return data

df_preprocessed = pd.read_csv("static/csv/Labeling_Hasil_Crawling_Berita.csv")

#Cleanning
def cleanning(text):
    return re.sub('[^a-zA-z\s]','', text) 

df_preprocessed['Title'] = df_preprocessed['Title'].apply(cleanning)

#remove number
def remove_number(text):
    return  re.sub(r"\d+", "", text)

    
df_preprocessed['Title'] = df_preprocessed['Title'].apply(remove_number)

# remove single char
def remove_singl_char(text):
    return re.sub(r"\b[a-zA-Z]\b", "", text)

df_preprocessed['Title'] = df_preprocessed['Title'].apply(remove_singl_char)

#remove punctuation
def remove_punctuation(text):
    return text.translate(str.maketrans("","",string.punctuation))

df_preprocessed['Title'] = df_preprocessed['Title'].apply(remove_punctuation)

# jalankan cleansing data
title_berita = []
for index, row in df_preprocessed.iterrows():
    title_berita.append(cleansing(row["Title"]))

df_preprocessed["Case_Folding"] = title_berita

# NLTK word rokenize 
def tokenizing(text):
    word_tokenize = re.split('\W+', text)
    return word_tokenize

df_preprocessed['Hasil_Token'] = df_preprocessed['Case_Folding'].apply(tokenizing)

# Tahap Filtering(Stopword)

# ----------------------- get stopword from NLTK stopword -------------------------------
# get stopword indonesia
list_stopwords = stopwords.words('indonesian')


# ---------------------------- manualy add stopword  ------------------------------------
# append additional stopword
list_stopwords.extend(["yg", "dg", "rt", "dgn", "ny", "d", 'klo', 
                    'kalo', 'amp', 'biar', 'bikin', 'bilang', 
                    'gak', 'ga', 'krn', 'nya', 'nih', 'sih', 
                    'si', 'tau', 'tdk', 'tuh', 'utk', 'ya', 
                    'jd', 'jgn', 'sdh', 'aja', 'n', 't', 
                    'nyg', 'hehe', 'pen', 'u', 'nan', 'loh', 'rt',
                    '&amp', 'yah'])


# convert list to dictionary
list_stopwords = set(list_stopwords)

#remove stopword pada list token
def stopwords_removal(words):
    return [word for word in words if word not in list_stopwords]

df_preprocessed['Hasil_Stopword'] = df_preprocessed['Hasil_Token'].apply(stopwords_removal)

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# stemmed
def stemmed_wrapper(term):
    return stemmer.stem(term)

term_dict = {}

for document in df_preprocessed['Hasil_Stopword']:
    for term in document:
        if term not in term_dict:
            term_dict[term] = ' '

for term in term_dict:
    term_dict[term] = stemmed_wrapper(term)

# apply stemmed term to dataframe
def get_stemmed_term(document):
    return [term_dict[term] for term in document]

df_preprocessed['Hasil_Stemming'] = df_preprocessed['Hasil_Stopword'].swifter.apply(get_stemmed_term)

df_preprocessed.to_csv("static/csv/text_processing.csv")

