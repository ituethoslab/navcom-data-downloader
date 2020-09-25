from navcom_data_downloader import app
from config import RedditCredentials, RedditConfig
import warnings
import praw
import pandas as pd
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

    def query(self, query, max=10):
        app.logger.debug(f"Querying Twitter for '{query}'")
        tweets = self._query(query, max=max)
        output = self._as_csv(tweets)
        return output

    def _query(self, query, max=10):
        twitter_query = got.manager.TweetCriteria()
        # Twitter won't accept empty query but will return 400 Bad Request.
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
        cols = ['id', 'permalink', 'username', 'text',
                'date', 'retweets', 'hashtags']
        output = io.StringIO()
        dict_writer = csv.DictWriter(output, cols, extrasaction='ignore')

        dict_writer.writeheader()
        for tweet in tweets:
            dict_writer.writerow(tweet.__dict__)

        output_str = output.getvalue()

        return output_str


class RedditDataSource(DataSource):
    """Model for Reddit datasource.

    Using the PRAW library. Warnings about unclosed SSL connections
    are ignored.
    """
    def __init__(self):
        super().__init__()
        app.logger.debug(f"  ... as a Reddit DataSource instantiated")
        self.reddit = praw.Reddit(client_id=RedditCredentials.client_id,
                                  client_secret=RedditCredentials.client_secret,
                                  password=RedditCredentials.password,
                                  user_agent=RedditCredentials.user_agent,
                                  username=RedditCredentials.username)

    def get_submission(self, submission_id):
        """Get a table of comments of a single submission.

        Parameters:
        submission_id (str): ID of Reddit submission to get

        Returns:
        str: String representation as CSV
        """
        submission = self._get_submission(submission_id)
        return self._as_csv([submission])

    def _get_submission(self, submission_id):
        """Get an individual submission and its comments."""
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            submission = self.reddit.submission(id=submission_id)
            submission.comments.replace_more(limit=RedditConfig.comment_limit)

        return submission

    def get_hot(self, subreddit, limit=RedditConfig.limit):
        """Get a table of comments of hot submissions from a subreddit.

        Parameters:
        subreddit (str): Subreddit to get from
        limit (int): Max number of submissions to get

        Returns:
        str: String representation as CSV
        """
        app.logger.debug(f"Querying Reddit for hot in {subreddit}")
        submissions = self._query(subreddit, 'hot', limit=limit)

        return self._as_csv(submissions)

    def get_new(self, subreddit, limit=RedditConfig.limit):
        """Get a table of comments of new submissions from a subreddit.

        Parameters:
        subreddit (str): Subreddit to get from
        limit (int): Max number of submissions to get

        Returns:
        str: String representation as CSV
        """
        app.logger.debug("Querying Reddit for new in {subreddit}")
        submissions = self._query(subreddit, 'new', limit=limit)

        return self._as_csv(submissions)

    def get_top(self, subreddit, limit=RedditConfig.limit):
        raise NotImplementedError


    def _query(self, subreddit, kind, limit=RedditConfig.limit):
        app.logger.debug(f"Querying Reddit {subreddit} for '{kind}'")
        subreddit = self.reddit.subreddit(subreddit)

        if kind == 'hot':
            submissions = subreddit.hot(limit=limit)

        if kind == 'new':
            submissions = subreddit.new(limit=limit)

        if kind == 'top':
            raise NotImplementedError("Needs a view.")

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            resolved_submissions = list(submissions)

        # Retrieve more comments.
        for submission in resolved_submissions:
            if any([isinstance(c, praw.models.MoreComments) for c in submission.comments]):
                app.logger.debug("Retrieving more comments for %s", submission.id)
                submission.comments.replace_more()

        app.logger.debug("Used %s API calls, %s remaining.",
                         self.reddit.auth.limits['used'],
                         self.reddit.auth.limits['remaining'])

        # return list(submissions)
        return resolved_submissions

    def _as_csv(self, submissions):
        """Format posts as CSV.

        Actually maybe this ought to be in a view, not here in the model."""
        app.logger.debug(f"Serializing {submissions}")
        columns = ['header', 'comments', 'author', 'created_utc', 'edited',
                   'score', 'is_submitter', 'parent_id', 'stickied']

        joined = [{**vars(s), **vars(c)} for s in submissions for c in s.comments]
        app.logger.debug(f"Joined a {len(joined)} dict.")
        df = pd.DataFrame.from_records(joined)
        app.logger.debug(f"Constructed an temp {df.shape} DataFrame")
        df = df.rename(columns={'title': 'header', 'body': 'comments'})
        df['comments'] = df['comments'].str.replace('\n', ' ')

        # Project to desired columns.
        projected_df = df[columns]
        return projected_df.to_csv(index=False)
