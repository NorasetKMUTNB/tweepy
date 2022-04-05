import os
import tweepy as tw
import pandas as pd
import re
from datetime import datetime, timedelta

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import isthai

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

import langdetect

from Sentiment import Sentiment
senti = Sentiment()
from Counting import Counting
count = Counting()

################################################################

class TwitterManger:
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
        directory = key
        # Parent Directory path
        parent_dir = "C://yaengg\DNS//tweepy//backup"
        
        # Path
        path = os.path.join(parent_dir, directory)
        
        # Create the directory
        # directory in parent_dir
        os.mkdir(path)

        # Create the directory
        # directory in parent_dir
        date_path = os.path.join(parent_dir, directory, 'file_date')
        os.mkdir(date_path)

        print("Directory '% s' created" %directory)

    ################################################################
    # Serach Tweet A Day
    ################################################################

    def new_data_aday(self, keyword, until):
        query = keyword
        new_search = query + " -filter:retweets"

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
            tweet_mode='extended').items(1000):

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
                keyword, 
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
            tweet_mode='extended').items(1000):

            # create_at = tweet.created_at.astimezone()
            create_at = tweet.created_at

            if create_at > startDate: continue
            elif create_at < endDate : break
            
            keyword = query
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
                keyword, 
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
        df.to_csv('backup//{}//file_date//{}_{}_twitterCrawler.csv'.format(keyword, keyword, until), index=False, encoding='utf-8')
        print('finished : {} at {}'.format(keyword, until))

    ################################################################
    # Serach Tweet Until
    ################################################################

    def serach_tweet(self, key, sta, end):
        i = 0
        end_date_obj = datetime.strptime(end, '%Y-%m-%d')

        while True:
            until_obj   = datetime.strptime(sta, '%Y-%m-%d') + timedelta(days=i)
            date        = until_obj.strftime("%Y-%m-%d") # str

            # break out loop
            if until_obj > end_date_obj:break

            self.new_data_aday(key, date)
            i+=1
        
        # union file_date
        self.union_file(key)

        # # collect counting
        count.BoW_tweet(key)
        count.count_hashtag(key)


    ################################################################
    # Union File Collect date
    ################################################################

    def union_file(key):
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

        print(key+' union finished')
        return list_date