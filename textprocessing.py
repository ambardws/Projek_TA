import pandas as pd
from pprint import pp, pprint
import string, re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import swifter


def textprocessing():
    df_preprocessed = pd.read_csv("static/csv/Hasil_Crawling_Berita.csv")
    def cleansing(data):
        # lower text
        data = data.lower()

        return data

    # jalankan cleansing data
    title_berita = []
    for index, row in df_preprocessed.iterrows():
        title_berita.append(cleansing(row["Title"]))
        
    df_preprocessed["Hasil_Case_Folding"] = title_berita
    
    #remove number
    def remove_number(text):
        return  re.sub(r"\d+", "", text)

    df_preprocessed['Hasil_Case_Folding'] = df_preprocessed['Hasil_Case_Folding'].apply(remove_number)

    #Cleanning
    def cleanning(text):
        return re.sub('[^a-zA-z\s]','', text) 

    df_preprocessed['Hasil_Case_Folding'] = df_preprocessed['Hasil_Case_Folding'].apply(cleanning)

    #remove punctuation
    def remove_punctuation(text):
        return text.translate(str.maketrans("","",string.punctuation))

    df_preprocessed['Hasil_Case_Folding'] = df_preprocessed['Hasil_Case_Folding'].apply(remove_punctuation)

    # remove whitespace leading & trailing
    def remove_whitespace_LT(text):
        return text.strip()

    df_preprocessed['Hasil_Case_Folding'] = df_preprocessed['Hasil_Case_Folding'].apply(remove_whitespace_LT)

    #remove multiple whitespace into single whitespace
    def remove_whitespace_multiple(text):
        return re.sub('\s+',' ',text)

    df_preprocessed['Hasil_Case_Folding'] = df_preprocessed['Hasil_Case_Folding'].apply(remove_whitespace_multiple)

    # remove single char
    def remove_singl_char(text):
        return re.sub(r"\b[a-zA-Z]\b", "", text)

    df_preprocessed['Hasil_Case_Folding'] = df_preprocessed['Hasil_Case_Folding'].apply(remove_singl_char)

    # NLTK word rokenize 
    def tokenizing(text):
        word_tokenize = re.split('\W+', text)
        return word_tokenize

    df_preprocessed['Hasil_Token'] = df_preprocessed['Hasil_Case_Folding'].apply(tokenizing)


    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary

    factory = StopWordRemoverFactory().get_stop_words()
    more_stopword = ['vaksin','vaksinasi','covid','corona','divaksin','divaksinasi']

    data = factory + more_stopword
    dictionary = ArrayDictionary(data)
    stopword = StopWordRemover(dictionary)

    df_preprocessed['Hasil_Stopword'] = df_preprocessed['Hasil_Case_Folding'].apply(lambda x: " ".join(stopword.remove(x) for x in x.split()))
    df_preprocessed['Hasil_Stopword'] = df_preprocessed['Hasil_Stopword'].apply(tokenizing)


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
