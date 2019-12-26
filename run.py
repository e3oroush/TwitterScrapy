'''
This Script uses Scrapy and Advanced Twitter search method for crawling Twitter
Twitter: @sentalysa
Email: sentalysa@gmail.com
'''
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from TweetScraper.spiders.TweetCrawler import TweetScraper
from scrapy.utils.project import get_project_settings
import argparse, datetime, math,sys
import configparser 

SETTINGS = get_project_settings() 

parser = argparse.ArgumentParser()
parser.add_argument('--outputFilename', 
help='Name of output file name without its extenstion', default='output.jl')
parser.add_argument('--query', help="Search query of twitter advanced search. \
            Note: You should only enter your query search here. \
            The query search should not contain ',' character  ", default='')
parser.add_argument('--lang', help='Language of retrieved tweets.', default='en')
parser.add_argument('--since', help='Starting date of period in search, pattern: yyyy-mm-dd',
 default='2013-01-01')
parser.add_argument('--until', help='End date of period in search, pattern: yyyy-mm-dd',
 default=None)
parser.add_argument('--fromAccount', help='Tweets from account name')
parser.add_argument('--toAccount', help='Tweets replying to the account')
parser.add_argument('--maxTweets', help='Max number of retrieved tweets', type=int, default=-1)
parser.add_argument('--numberOfConcurrentCrawler',
 help='Number of concurrent crawler for crawling to website', type=int, default=4)
parser.add_argument('--textOnly',
 help='Boolean input: True/False if you want to store just text with ID', type=bool, default=False)
parser.add_argument('--configFile', help='Address of config file', default='')
args = parser.parse_args()
if __name__ == '__main__':
    if not args.configFile:
        config = configparser.SafeConfigParser()
        config.optionxform = str
        config.add_section('Defaults')
        for arg in vars(args):
            if getattr(args, str(arg)):
                config.set('Defaults', arg, str(getattr(args, str(arg))))
            else:
                config.set('Defaults', arg, '')
        with open('config.ini', 'w') as f:
            config.write(f)

    if args.configFile:
        config = configparser.SafeConfigParser()
        config.optionxform = str
        config.read([args.configFile])
        defaults = dict(config.items("Defaults"))
        parser.set_defaults(**defaults)
        args = parser.parse_args()
    since = args.since
    until = args.until
    from_account = args.fromAccount
    to_account = args.toAccount
    SETTINGS['OUTPUT_FILENAME'] = str(args.outputFilename)
    SETTINGS['MAX_TWEETS'] = args.maxTweets
    SETTINGS['TEXT_ONLY'] = args.textOnly
    process = CrawlerProcess(get_project_settings())
    since = datetime.datetime(*[int(i) for i in since.split('-')])
    if not until:
        until = datetime.datetime.now().strftime("%Y-%m-%d")
    until = datetime.datetime(*[int(i) for i in until.split('-')])
    diff = (until - since).days
    days_in_process = math.ceil(diff/args.numberOfConcurrentCrawler)
    query = args.query
    if from_account:
        query += ',from:%s'%from_account
    if to_account:
        query += ',to:%s'%to_account
    for i in range(args.numberOfConcurrentCrawler - 1):
        until_crawler = since + datetime.timedelta(days_in_process-1)
        process.crawl(TweetScraper, query='%s,since:%s,until:%s'%(query, since.date(), until_crawler.date()), lang=args.lang)
        since += datetime.timedelta(days_in_process)
    process.crawl(TweetScraper, query='%s,since:%s,until:%s'%(query, since.date(), until.date()), lang=args.lang)
    process.start() # the script will block here until the crawling is finished