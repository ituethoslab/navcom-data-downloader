from navcom_data_downloader import app
from datetime import datetime
import GetOldTweets3 as got
import csv
import io

class DataSource():
    """An \"abstract\" datasource. Inherit from this."""
    def __init__(self):
        app.logger.debug(f"Generic DataSource instantiated")

    def query(self, query):
        app.logger.debug("Would query for '{query}'")
        ...

    def _as_csv(self, data):
        ...


class TwitterDataSource(DataSource):
    """Model for a Twitter datasource."""
    def __init__(self):
        super().__init__()
        app.logger.debug(f"  ... as a Twitter DataSource instantiated")

    def query(self, query, max = 10):
        app.logger.debug(f"Querying Twitter for '{query}'")
        tweets = self._query(query, max = max)
        output = self._as_csv(tweets)
        return output

    def _query(self, query, max = 10):
        twitter_query = got.manager.TweetCriteria()
        # Twitter won't accept empty query string but will return 400 Bad Request.
        twitter_query.setQuerySearch(query['string'])
        if 'start-date' in query:
            twitter_query.setSince(query['start-date'])
        if 'end-date' in query:
            twitter_query.setUntil(query['end-date'])
        twitter_query.setMaxTweets(max)

        tweets = got.manager.TweetManager.getTweets(twitter_query)
        app.logger.debug(tweets)

        return tweets

    def _as_csv(self, tweets):
        """Format whatever comes out from the source as CSV."""
        cols = ['id', 'permalink', 'username', 'text', 'date', 'retweets', 'hashtags']
        output = io.StringIO()
        dict_writer = csv.DictWriter(output, cols, extrasaction='ignore')
        
        dict_writer.writeheader()
        for tweet in tweets:
            dict_writer.writerow(tweet.__dict__)

        output_str = output.getvalue()
            
        return output_str
