import os
import tweepy as tw
import pandas as pd
import re

from datetime import datetime, timedelta

import sys
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import isthai

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

from Sentiment import Sentiment
senti = Sentiment()
from Counting import Counting
count = Counting()

from dialog_gui import *

################################################################
## TwitterManager Class
################################################################
class twitter_manager:
    def __init__(self):
        # Consumer Key = API Key
        self.consumer_key= '7wlWBiho3eO8BnNQihvZptNHl'   
        # Consumer Secret = API Secret
        self.consumer_secret= 'd4LRXmrOOhL7V3ZdPeSHYh2QCsvt9rfJLKF9WfffTUVY1sfzoR'
        # OAuth Token = Access Token
        self.access_token= '824220293111500800-lO5uQ3dlEoVIQ6cjadV6JGV0iKDjGAp'
        # OAuth Token Secret = Access Token Secret
        self.access_token_secret= 'h2r1uSEtEp7Mo5z6tb7LLM3mbE559hD1W9v3aa8vladTZ'

        self.auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        # get twiiter_API
        self.api = tw.API(self.auth, wait_on_rate_limit=True)

    
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
    # Create Dicectory
    ################################################################
    def create_directory(self, key):
    # Directory
        self.key = key
        # Parent Directory path
        parent_dir = "C://yaengg\DNS//tweepy//backup"
        
        # Path
        path = os.path.join(parent_dir, self.key)
        
        # Create the directory
        # directory in parent_dir
        os.mkdir(path)

        # Create the directory
        # directory in parent_dir
        date_path = os.path.join(parent_dir, self.key, 'file_date')
        os.mkdir(date_path)

        print("Directory '% s' created" %self.key)

    ################################################################
    # Serach Tweet A Day
    ################################################################
    def new_data_aday(self, key, until):
        self.key = key
        new_search = self.key + " -filter:retweets"

        until_obj   = datetime.strptime(until, '%Y-%m-%d') + timedelta(days=1)
        until_set   = until_obj.strftime("%Y-%m-%d")

        # startDate   = datetime.strptime(until+'23:59:59', '%Y-%m-%d%H:%M:%S').astimezone()
        startDate   = datetime.strptime(until+'23:59:59+00:00', '%Y-%m-%d%H:%M:%S%z')
        endDate     = startDate - timedelta(days=1)

        df = pd.DataFrame(columns= [
            'keyword',
            'language',
            'author',
            'twitter_name',
            'create_at',
            'location', 
            'text', 
            'hashtag', 
            'tweets_count',
            'retweet_count', 
            'favourite_count',
            'date',
            'time',
            'sentiment'])

        columns = [
            'keyword',
            'language',
            'author',
            'twitter_name',
            'create_at', 
            'location',
            'text', 
            'hashtag', 
            'tweets_count',
            'retweet_count', 
            'favourite_count',
            'date',
            'time',
            'sentiment']

        ############################################################
        # twitter(TH)
        ############################################################
        for tweet in tw.Cursor(self.api.search_tweets,
            q=new_search,
            lang='th',
            until=until_set,
            result_type='recent',
            tweet_mode='extended').items(100):

            # create_at = tweet.created_at.astimezone()
            create_at = tweet.created_at

            if create_at > startDate: continue
            elif create_at < endDate : break

            # keyword = query
            language = 'th'
            tweets_count = 1

            # hashtag
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ''
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'/'+entity_hashtag[i]['text']

            # infomantion
            twitter_name = '@'+tweet.user.screen_name
            author = tweet.user.name
            location = tweet.user.location
            re_count = tweet.retweet_count
            tweets_count += re_count
            
            date = create_at.strftime("%d/%m/%Y")
            time = create_at.strftime("%H:%M")

            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            sentiment = senti.checksentimentword(self.remove_url_th(text))

            # temp for a tweet in data_frame
            new_column = pd.DataFrame([[
                self.key, 
                language, 
                author,
                twitter_name,
                create_at, 
                location,
                text, 
                hashtag, 
                tweets_count, 
                re_count,
                fav_count, 
                date,
                time,
                sentiment]], columns = columns)

            # append in data_frame
            df = pd.concat([df,new_column],ignore_index=True)

        ############################################################
        # twitter(EN)
        ############################################################
        for tweet in tw.Cursor(self.api.search_tweets,
            q=new_search,
            lang='en',
            until=until_set,
            result_type='recent',
            tweet_mode='extended').items(100):

            # create_at = tweet.created_at.astimezone()
            create_at = tweet.created_at

            if create_at > startDate: continue
            elif create_at < endDate : break
            
            # keyword = self.key
            language = 'en'
            tweets_count = 1

            # hashtag
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ''
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +'/'+entity_hashtag[i]['text']

            # infomantion
            twitter_name = '@'+tweet.user.screen_name
            author = tweet.user.name
            location = tweet.user.location
            re_count = tweet.retweet_count
            tweets_count += re_count

            date = create_at.strftime("%d/%m/%Y")
            time = create_at.strftime("%H:%M")

            try:
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count

            sentiment = senti.checksentimentword(self.remove_url_th(text))

            new_column = pd.DataFrame([[
                self.key, 
                language, 
                author,
                twitter_name,
                create_at, 
                location,
                text, 
                hashtag, 
                tweets_count, 
                re_count,
                fav_count, 
                date,
                time,
                sentiment]], columns = columns)

            # append in data_frame
            df = pd.concat([df,new_column],ignore_index=True)

        # convent to csv
        df.to_csv('backup//{}//file_date//{}_{}_twitterCrawler.csv'.format(self.key, self.key, until), index=False, encoding='utf-8')
        # print('finished : {} at {}'.format(self.key, until))

    ################################################################
    # Union File Collect date
    ################################################################
    def union_file(self, key):
        path = ".//backup//{}//file_date".format(key)

        df = pd.DataFrame(columns= [
            'keyword',
            'language',
            'author',
            'twitter_name',
            'create_at',
            'location', 
            'text', 
            'hashtag', 
            'tweets_count',
            'retweet_count',
            'favourite_count',
            'date',
            'time',
            'sentiment'])

        list_date = []

        for x in os.listdir(path):
            if x.endswith(".csv"):
                # Prints only text file present in My Folder
                x = x.replace('.csv', '')
                # print(x)
                list_date.append(x.split("_")[1])

                temp_df = pd.read_csv('.//backup//{}//file_date//{}.csv'.format(key ,x))
                df = pd.concat([df,temp_df],ignore_index=True)

                # convent to csv
                df.to_csv('.//backup//{}//{}.csv'.format(key, key), index=False, encoding='utf-8')
        # print(key+' union finished')

################################################################
## WorkerThread Class
################################################################

################################################################
## WorkerTweet Class
################################################################
class WorkerTweet(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # self.key = self.parent.key

        self.twm = twitter_manager()
        self.count = Counting()

    def run(self):
        i = 0
        self.key = self.parent.key
        begin_date_obj = datetime.strptime(self.parent.begin_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(self.parent.end_date, '%Y-%m-%d')
        count_progress = (end_date_obj - begin_date_obj).days + 1 

        while True:
            until_obj   = datetime.strptime(self.parent.begin_date, '%Y-%m-%d') + timedelta(days=i)
            date        = until_obj.strftime("%Y-%m-%d") # str

            # break out loop
            if until_obj > end_date_obj:break

            # progress label
            self.parent.pbar.set_progress_label('Crawler {}'.format(date))
            self.twm.new_data_aday(self.key, date)

            i += 1
            self.update_progress.emit((i/count_progress)*100)

        # Union file_date
        self.parent.pbar.set_progress_label('Union {}'.format(self.key))
        self.twm.union_file(self.key)
        self.update_progress.emit(100)
        print('{} Union finished'.format(self.key))

        # BOW file_date
        self.parent.pbar.set_progress_label('BOW {}'.format(self.key))
        self.count.BoW_tweet(self.key)
        self.update_progress.emit(100)
        print('{} Word finished'.format(self.key))

        # Hashtag file_date
        self.parent.pbar.set_progress_label('Hashtag {}'.format(self.key))
        self.count.count_hashtag(self.key)
        self.update_progress.emit(100)
        print('{} Hastag finished'.format(self.key))

        self.exit()

    def stop(self):
        print('Stop Worker Tweet')
        self.terminate()


################################################################
## WorkerCSV Class
################################################################
class WorkerCSV(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        """ This method will make all table """
        key = self.parent.key
        print("Thread Worker CSV :", key, " runing...")
        ### base_table ###
        self.parent.ui.base_label.setText("{}".format(key))
        df_base = pd.read_csv('.//backup//{}//{}.csv'.format(key, key))

        # progress label
        self.parent.pbar.set_progress_label('Open Base {} file'.format(key))

        len_row_base = len(df_base.index)
        len_col_base = len(df_base.columns)

        self.parent.ui.base_table.setColumnCount(len_col_base)
        self.parent.ui.base_table.setRowCount(len_row_base)
        self.parent.ui.base_table.setHorizontalHeaderLabels(df_base.columns)

        pbar_count = 0
        self.update_progress.emit(pbar_count)
        for i in range(len_row_base):
            for j in range(len_col_base):
                self.parent.ui.base_table.setItem(i ,j, QTableWidgetItem(str(df_base.iat[i, j])))
            pbar_count = int((i/len_row_base)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.base_table.resizeColumnsToContents()
        self.parent.ui.status_base_label.setText("{} Tweets".format(len_row_base))

        ### word_table ###
        self.df_word = pd.read_csv('.//backup//{}//{}_count_word.csv'.format(key, key))

        # progress label
        self.parent.pbar.set_progress_label('Open BOW {} file'.format(key))

        len_row_word = len(self.df_word.index)
        len_col_word = len(self.df_word.columns)

        self.parent.ui.word_table.setColumnCount(len_col_word)
        self.parent.ui.word_table.setRowCount(len_row_word)
        self.parent.ui.word_table.setHorizontalHeaderLabels(self.df_word.columns)

        pbar_count = 0
        for i in range(len_row_word):
            for j in range(len_col_word):
                self.parent.ui.word_table.setItem(i ,j, QTableWidgetItem(str(self.df_word.iat[i, j])))
            # update progress bar
            pbar_count = int((i/len_row_word)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.word_table.resizeColumnsToContents()
        self.parent.ui.status_word_label.setText("{} Words".format(len_row_word))

        ### hashtag_table ###
        self.df_hashtag = pd.read_csv('.//backup//{}//{}_count_hashtag.csv'.format(key, key))

        # progress label
        self.parent.pbar.set_progress_label('Open Hashtag {} file'.format(key))

        len_row_hashtag = len(self.df_hashtag.index)
        len_col_hashtag = len(self.df_hashtag.columns)

        self.parent.ui.hashtag_table.setColumnCount(len_col_hashtag)
        self.parent.ui.hashtag_table.setRowCount(len_row_hashtag)
        self.parent.ui.hashtag_table.setHorizontalHeaderLabels(self.df_hashtag.columns)

        pbar_count = 0
        for i in range(len_row_hashtag):
            for j in range(len_col_hashtag):
                self.parent.ui.hashtag_table.setItem(i ,j, QTableWidgetItem(str(self.df_hashtag.iat[i, j])))
            # update progress bar
            pbar_count = int((i/len_row_hashtag)*100)
            self.update_progress.emit(pbar_count)

        self.parent.ui.hashtag_table.resizeColumnsToContents()
        self.parent.ui.status_hashtag_label.setText("{} Hashtags".format(len_row_hashtag))

    def stop(self):
        print('Stop Worker CSV')
        self.terminate()

################################################################
## WorkerChangeDate Class
################################################################
class WorkerChangeDate(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.count = Counting()

    def run(self):
        temp_count = 0
        value = self.parent.DateSelection
        self.key = self.parent.key

        # progress label
        self.parent.pbar.set_progress_label('Open Base {} file'.format(self.key))
        self.parent.ui.base_table.setRowCount(0)        # clear table base

        if value == 'All':
            for i in self.parent.dict_date:
                if not self.parent.dict_date[i] :
                    self.df_base = pd.DataFrame(columns= [
                        'keyword',
                        'language',
                        'author',
                        'twitter_name',
                        'create_at',
                        'location', 
                        'text', 
                        'hashtag', 
                        'tweets_count',
                        'retweet_count',
                        'favourite_count',
                        'date',
                        'time',
                        'sentiment'])
                    for j in self.parent.list_date[1:]:
                        temp_df = pd.read_csv('.//backup//{}//file_date//{}_{}_twitterCrawler.csv'.format(self.key ,self.key, j))
                        self.df_base = pd.concat([self.df_base,temp_df],ignore_index=True)
                    break
                else: 
                    temp_count += 1

            if temp_count == len(self.parent.dict_date):
                self.df_base = pd.read_csv('.//backup//{}//{}.csv'.format(self.key, self.key))

            len_row_base = len(self.df_base.index)
            len_col_base = len(self.df_base.columns)

            self.parent.ui.base_table.setColumnCount(len_col_base)
            self.parent.ui.base_table.setRowCount(len_row_base)
            self.parent.ui.base_table.setHorizontalHeaderLabels(self.df_base.columns)

            # add data in table
            pbar_count = 0
            self.update_progress.emit(pbar_count)
            for i in range(len_row_base):
                for j in range(len_col_base):
                    self.parent.ui.base_table.setItem(i ,j, QTableWidgetItem(str(self.df_base.iat[i, j])))
                pbar_count = int((i/len_row_base)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.base_table.resizeColumnsToContents()
            self.parent.ui.status_base_label.setText("{} Tweets".format(len_row_base))

        elif value != '':
            self.df_base = pd.read_csv('.//backup//{}//file_date//{}_{}_twitterCrawler.csv'.format(self.key, self.key, value))

            len_row_base = len(self.df_base.index)
            len_col_base = len(self.df_base.columns)

            self.parent.ui.base_table.setColumnCount(len_col_base)
            self.parent.ui.base_table.setRowCount(len_row_base)
            self.parent.ui.base_table.setHorizontalHeaderLabels(self.df_base.columns)

            # add data in table
            pbar_count = 0
            self.update_progress.emit(pbar_count)
            for i in range(len_row_base):
                for j in range(len_col_base):
                    self.parent.ui.base_table.setItem(i ,j, QTableWidgetItem(str(self.df_base.iat[i, j])))
                pbar_count = int((i/len_row_base)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.base_table.resizeColumnsToContents()
            self.parent.ui.status_base_label.setText("{} Tweets".format(len_row_base))


        self.parent.ui.word_table.setRowCount(0)        # clear table word
        self.parent.ui.hashtag_table.setRowCount(0)     # clear table hashtag


        # all date 
        if temp_count == len(self.parent.dict_date):
            ### word_table ###
            self.df_word = pd.read_csv('.//backup//{}//{}_count_word.csv'.format(self.key, self.key))

            # progress label
            self.parent.pbar.set_progress_label('Open BOW {} file'.format(self.key))

            len_row_word = len(self.df_word.index)
            len_col_word = len(self.df_word.columns)

            self.parent.ui.word_table.setColumnCount(len_col_word)
            self.parent.ui.word_table.setRowCount(len_row_word)
            self.parent.ui.word_table.setHorizontalHeaderLabels(self.df_word.columns)

            pbar_count = 0
            for i in range(len_row_word):
                for j in range(len_col_word):
                    self.parent.ui.word_table.setItem(i ,j, QTableWidgetItem(str(self.df_word.iat[i, j])))
                # update progress bar
                pbar_count = int((i/len_row_word)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.word_table.resizeColumnsToContents()
            self.parent.ui.status_word_label.setText("{} Words".format(len_row_word))

            ### hashtag_table ###
            self.df_hashtag = pd.read_csv('.//backup//{}//{}_count_hashtag.csv'.format(self.key, self.key))

            # progress label
            self.parent.pbar.set_progress_label('Open Hashtag {} file'.format(self.key))

            len_row_hashtag = len(self.df_hashtag.index)
            len_col_hashtag = len(self.df_hashtag.columns)

            self.parent.ui.hashtag_table.setColumnCount(len_col_hashtag)
            self.parent.ui.hashtag_table.setRowCount(len_row_hashtag)
            self.parent.ui.hashtag_table.setHorizontalHeaderLabels(self.df_hashtag.columns)

            pbar_count = 0
            for i in range(len_row_hashtag):
                for j in range(len_col_hashtag):
                    self.parent.ui.hashtag_table.setItem(i ,j, QTableWidgetItem(str(self.df_hashtag.iat[i, j])))
                # update progress bar
                pbar_count = int((i/len_row_hashtag)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.hashtag_table.resizeColumnsToContents()
            self.parent.ui.status_hashtag_label.setText("{} Hashtags".format(len_row_hashtag))

        # Not all date must have new BOW and Hashtag
        elif not (self.df_base.empty) :
            # BOW work
            # progress label
            self.parent.pbar.set_progress_label('Open BOW {} file'.format(self.key))

            new_text = []
            for txt in self.df_base["text"]:
                new_text.append(self.count.cleanText(txt))
        
            self.df_word = pd.DataFrame(columns = ['word', 'count_word'])

            vectorizer = CountVectorizer(tokenizer=self.count.tokenize)   
            transformed_data = vectorizer.fit_transform(new_text)
            self.df_word['word'] = vectorizer.get_feature_names_out()

            # inserting column with static value in data frame
            self.df_word.insert(0,'keyword',self.key)
            self.count.language(self.df_word)

            # counting of word
            self.df_word['count_word'] = np.ravel(transformed_data.sum(axis=0))
            self.df_word = self.df_word.sort_values(by=['count_word'], ascending=False)

            ### word_table ###            
            len_row_word = len(self.df_word.index)
            len_col_word = len(self.df_word.columns)

            self.parent.ui.word_table.setColumnCount(len_col_word)
            self.parent.ui.word_table.setRowCount(len_row_word)
            self.parent.ui.word_table.setHorizontalHeaderLabels(self.df_word.columns)

            pbar_count = 0
            for i in range(len_row_word):
                for j in range(len_col_word):
                    self.parent.ui.word_table.setItem(i ,j, QTableWidgetItem(str(self.df_word.iat[i, j])))
                # update progress bar
                pbar_count = int((i/len_row_word)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.word_table.resizeColumnsToContents()
            self.parent.ui.status_word_label.setText("{} Words".format(len_row_word))

            # Hashtag work
            # progress label
            self.parent.pbar.set_progress_label('Open Hashtag {} file'.format(self.key))
            hastag_data = self.df_base["hashtag"].dropna()

            vectorizer = CountVectorizer(tokenizer=self.count.slash_tokenize)
            transformed_data = vectorizer.fit_transform(hastag_data)

            self.df_hashtag = pd.DataFrame(columns = ['hashtag', 'count']) 
            self.df_hashtag['hashtag'] = vectorizer.get_feature_names_out()
            self.df_hashtag.insert(0,'keyword',self.key)

            self.df_hashtag['count'] = np.ravel(transformed_data.sum(axis=0))

            self.df_hashtag = self.df_hashtag.sort_values(by=['count'], ascending=False)

            ### hashtag_table ###
            len_row_hashtag = len(self.df_hashtag.index)
            len_col_hashtag = len(self.df_hashtag.columns)

            self.parent.ui.hashtag_table.setColumnCount(len_col_hashtag)
            self.parent.ui.hashtag_table.setRowCount(len_row_hashtag)
            self.parent.ui.hashtag_table.setHorizontalHeaderLabels(self.df_hashtag.columns)

            pbar_count = 0
            for i in range(len_row_hashtag):
                for j in range(len_col_hashtag):
                    self.parent.ui.hashtag_table.setItem(i ,j, QTableWidgetItem(str(self.df_hashtag.iat[i, j])))
                # update progress bar
                pbar_count = int((i/len_row_hashtag)*100)
                self.update_progress.emit(pbar_count)

            self.parent.ui.hashtag_table.resizeColumnsToContents()
            self.parent.ui.status_hashtag_label.setText("{} Hashtags".format(len_row_hashtag))

    def stop(self):
        print('Stop Worker Change Date')
        self.terminate()
    