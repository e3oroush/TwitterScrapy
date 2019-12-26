# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
from scrapy.exceptions import CloseSpider
import logging
import json
import os
from scrapy import crawler
from subprocess import call
from TweetScraper.items import Tweet, TextTweet
from TweetScraper.utils import mkdirs
import sys
from scrapy.utils.project import get_project_settings
SETTINGS = get_project_settings()
# from scrapy.contrib.closespider import CloseSpider


logger = logging.getLogger(__name__)

class SaveToFilePipeline(object):
    ''' pipeline that save data to disk '''
    def __init__(self, save_tweet_path, output_filename, max_tweets):
        self.save_tweet_path = save_tweet_path
        self.tweet_counts = 0
        self.max_tweets = max_tweets
        self.output_filename = output_filename
        mkdirs(self.save_tweet_path) # ensure the path exists

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            save_tweet_path=crawler.settings.get('SAVE_TWEET_PATH'),
            output_filename=crawler.settings.get('OUTPUT_FILENAME'),
            max_tweets=crawler.settings.get('MAX_TWEETS')
        )

    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            savePath = os.path.join(self.save_tweet_path, self.output_filename)
            # self.save_to_file(item, savePath)
            # print("-----------------" + item)
            if(bool(SETTINGS['TEXT_ONLY'])):
                tweet = TextTweet()
                tweet['ID'], tweet['text'] = item['ID'], item['text']
                self.save_to_file(tweet, savePath)
            else:
                self.save_to_file(item, savePath)
        else:
            logger.info("Item type is not recognized! type = %s" %type(item))


    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname,'a', encoding='utf8') as f:
            json.dump(dict(item), f, ensure_ascii=False)
            f.write('\n')
        self.tweet_counts += 1
        if(self.tweet_counts == int(self.max_tweets)):
            call(['kill', '9', '%d'%os.getpid()])
            

