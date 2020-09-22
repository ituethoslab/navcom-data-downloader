from navcom_data_downloader import app
from datetime import datetime
from config import RedditCredentials
import pandas as pd
import praw
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


class RedditDataSource(DataSource):
    """Model for Reddit datasource.

    Using the PRAW library."""
    def __init__(self):
        super().__init__()
        app.logger.debug(f"  ... as a Reddit DataSource instantiated")
        creds = RedditCredentials()
        self.reddit = praw.Reddit(client_id=creds.client_id,
                                  client_secret=creds.client_secret,
                                  password=creds.password,
                                  user_agent=creds.user_agent,
                                  username=creds.username)

    def get_submission(self, submission_id):
        """Get an individual submission and its comments."""
        submission = self.reddit.submission(id=submission_id)
        submission.comments.replace_more(limit=None)
        return submission

    def get_hot(self, subreddit, limit = 10):
        app.logger.debug(f"Querying Reddit for hot in {subreddit}")
        submissions = self._query(subreddit, 'hot', limit = limit)

        return submissions

    def get_new(self, subreddit, limit = 10):
        app.logger.debug("Querying Reddit for new in {subreddit}")
        submissions = self._query(subreddit, 'new', limit = limit)

        return submissions

    def get_top(self, subreddit, limit = 10):
        raise NotImplementedError

    def _query(self, subreddit, kind, limit = 10):
        app.logger.debug(f"Querying Reddit {subreddit} for '{kind}'")
        subreddit = self.reddit.subreddit(subreddit)
        if kind == 'hot':
            submissions = subreddit.hot(limit = limit)

        if kind == 'new':
            submissions = subreddit.new(limit = limit)

        if kind == 'top':
            raise NotImplementedError("Needs a view.")

        # Retrieve more comments.
        # for submission in submissions:
        #     submission.comments.replace_more()

        return list(submissions)

    def _as_csv(self, submissions):
        """Format posts as CSV:"""
        # pd.DataFrame.from_records([vars(c) for s in submissions for c in s.comments])
        # pd.DataFrame.from_records([vars(c) for s in submissions for c in s.comments])[['author', 'created_utc', 'edited', 'score', 'is_submitter', 'parent_id', 'stickied']]
        # pd.DataFrame.from_records([{**vars(s), **vars(c)} for s in submissions for c in s.comments])[['title', 'body', 'author', 'created_utc', 'edited', 'score', 'is_submitter', 'parent_id', 'stickied']]
        # Rather join on submission ID or something? with
        #    submissions[2].id == submissions[2].comments[0]._submission
        #    submissions[2].id == submissions[2].comments[0].submission.id
        columns = ['title', 'body', 'author', 'created_utc', 'edited',
                   'score', 'is_submitter', 'parent_id', 'stickied']

        joined = [{**vars(s), **vars(c)} for s in submissions for c in s.comments]
        df = pd.DataFrame.from_records(joined)
        df['body'] = df['body'].apply(lambda x : x.replace('\n',' '))

        return df[columns].to_csv()
