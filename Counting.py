
import os
import pandas as pd
import re

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import isthai

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

import langdetect

################################################################

class Counting:
    def __init__(self):
        pass

    def remove_url_th(self,txt):
        """Replace URLs found in a text string with nothing 
        (i.e. it will remove the URL from the string).

        Parameters
        ----------
        txt : string
            A text string that you want to parse and remove urls.

        Returns
        -------
        The same txt string with url's removed.
        """

        return " ".join(re.sub("([^\u0E00-\u0E7Fa-zA-Z' ]|^'|'$|''|(\w+:\/\/\S+))", "", txt).split())

    
    ################################################################
    # Bow
    ################################################################

    def BoW_tweet(self, key):
        df = pd.read_csv('backup//{}//{}.csv'.format(key, key))

        new_text = []
        for txt in df["text"]:
            new_text.append(self.cleanText(txt))

        keyword_df = pd.DataFrame(columns = ['word', 'count_word'])

        vectorizer = CountVectorizer(tokenizer=self.tokenize)   
        transformed_data = vectorizer.fit_transform(new_text)
        keyword_df['word'] = vectorizer.get_feature_names_out()

        # inserting column with static value in data frame
        keyword_df.insert(0,'keyword',key)
        self.language(keyword_df)

        # counting of word
        keyword_df['count_word'] = np.ravel(transformed_data.sum(axis=0))

        keyword_df = keyword_df.sort_values(by=['count_word'], ascending=False)
        keyword_df.to_csv('backup//{}//{}_count_word.csv'.format(key, key), index=False, encoding='utf-8')

    def language(self, data):
        temp_language = pd.Series([],dtype=pd.StringDtype())
        for i in range(len(data)):
            if isthai(data["word"][i]): temp_language[i]="th"
            else: temp_language[i]="en"
        data.insert(1, "language", temp_language)
        
    def cleanText(self, text):
        text = self.remove_url_th(text).lower()
        # check language
        if (langdetect.detect(text)) == 'th':
            text = self.remove_url_th(text)
            text = re.sub('[^ก-๙]','',text)
            stop_word = list(thai_stopwords())
            sentence = word_tokenize(text, engine="newmm")
            result = [word for word in sentence if word not in stop_word and " " not in word]
            return "/".join(result)
        else:
            stop_word = set(stopwords.words('english'))
            sentence = text.split()
            result = [word for word in sentence if word not in stop_word and  " " not in word]
            return "/".join(result)
    
    def tokenize(self, d):
        result = d.split("/")
        result = list(filter(None, result))
        return result
    
    ################################################################
    # hashtag
    ################################################################

    def count_hashtag(self, key):
        df = pd.read_csv('backup//{}//{}.csv'.format(key, key))

        hastag_data = df["hashtag"].dropna()

        vectorizer = CountVectorizer(tokenizer=self.slash_tokenize)
        transformed_data = vectorizer.fit_transform(hastag_data)

        hash_tag_cnt_df = pd.DataFrame(columns = ['hashtag', 'count']) 
        hash_tag_cnt_df['hashtag'] = vectorizer.get_feature_names_out()
        hash_tag_cnt_df.insert(0,'keyword',key)

        hash_tag_cnt_df['count'] = np.ravel(transformed_data.sum(axis=0))

        hash_tag_cnt_df = hash_tag_cnt_df.sort_values(by=['count'], ascending=False)

        hash_tag_cnt_df.to_csv('backup//{}//{}_count_hashtag.csv'.format(key, key), index=False, encoding='utf-8')
    
    def slash_tokenize(self, d):  
        result = d.split("/")
        result.remove('')
        return result