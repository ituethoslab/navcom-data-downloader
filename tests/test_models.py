import unittest
import datetime
import praw
import pandas as pd
from io import StringIO
from config import RedditCredentials
from navcom_data_downloader import app
from navcom_data_downloader.models import DataSource, TwitterDataSource, RedditDataSource

class TestDataSource(unittest.TestCase):
    def test_instantiating_generic_model_should_be_fine(self):
        ds = DataSource()
        self.assertIsInstance(ds, DataSource)


class TestTwitterDataSource(unittest.TestCase):
    def test_instantiating_should_be_fine(self):
        tds = TwitterDataSource()
        self.assertIsInstance(tds, TwitterDataSource)
    
    def test_querying_with_all_params_should_return_data(self):
        query = {'string': "giraffe",
                 'start-date': '2020-08-15',
                 'end-date': '2020-09-03'}
        tds = TwitterDataSource()
        data = tds._query(query)
        self.assertEqual(10, len(data))

    def test_querying_with_no_params_should_raise_an_error(self):
        query = {}
        tds = TwitterDataSource()
        with self.assertRaises(KeyError):
            data = tds._query(query)

    def test_query_with_only_string_should_be_sufficient(self):
        query = {'string': 'goats'}
        tds = TwitterDataSource()
        data = tds._query(query)
        self.assertEqual(10, len(data))

    def test_query_results_should_be_not_older_than_start_time(self):
        """Twitter sometimes returns tweets beyond the start-time."""
        start_date = datetime.datetime(2020, 6, 1, tzinfo=datetime.timezone.utc)
        query = {'string': "sheepie",
                 'start-date': str(start_date.date())}
        tds = TwitterDataSource()
        data = tds._query(query)
        self.assertTrue(all([datum.date >= start_date for datum in data]))

    def test_query_results_should_be_not_newer_than_end_time(self):
        """Twitter sometimes returns tweets beyond the end-time."""
        end_date = datetime.datetime(2020, 6, 1, tzinfo=datetime.timezone.utc)
        query = {'string': "owl",
                 'end-date': str(end_date.date())}
        tds = TwitterDataSource()
        data = tds._query(query)
        [print(str(datum.date), datum.permalink) for datum in data]
        self.assertTrue(all([datum.date <= end_date for datum in data]))


class TestRedditDataSource(unittest.TestCase):
    def setUp(self):
        self.rds = RedditDataSource()
        app.logger.setLevel('INFO')

    def test_instantiating_should_be_fine(self):
        self.assertIsInstance(self.rds, RedditDataSource)
        self.assertIsInstance(self.rds.reddit, praw.reddit.Reddit)

    def test_authentication_should_succeed(self):
        ...

    def test_getting_a_specific_submission_by_id_should_succeed(self):
        sid = '7jgnxm'
        submission = self.rds.get_submission(sid)
        self.assertEqual(sid, submission.id)

    def test_getting_hot_from_a_subreddit_should_succeed(self):
        subreddit = 'dataisbeautiful'
        submissions = self.rds.get_hot(subreddit, limit=3)
        self.assertTrue(all([submission.subreddit.display_name == subreddit for submission in submissions]))

    def test_getting_hot_from_a_subreddit_with_limit_should_limit_the_number_of_results(self):
        subreddit = 'dataisbeautiful'
        less_submissions = self.rds.get_hot(subreddit, limit=3)
        self.assertEqual(3, len(less_submissions))

        more_submissions = self.rds.get_hot(subreddit, limit=100)
        self.assertEqual(100, len(more_submissions))

    def test_serializing_a_single_submission_should_work(self):
        submission = self.rds.get_submission('7jgnxm')
        self.assertIsInstance(self.rds._as_csv([submission]), str)
        self.assertEqual(540, len(self.rds._as_csv([submission])))

    def test_serialized_single_submission_should_parse(self):
        submission = self.rds.get_submission('7jgnxm')
        df = pd.read_csv(StringIO(self.rds._as_csv([submission])))
        self.assertEqual(df.shape, (1, 10))

    def test_serialized_single_submission_should_have_expected_header(self):
        submission = self.rds.get_submission('7jgnxm')
        df = pd.read_csv(StringIO(self.rds._as_csv([submission])))
        self.assertEqual(list(df.columns), ['Unnamed: 0', 'title', 'body', 'author', 'created_utc', 'edited', 'score', 'is_submitter', 'parent_id', 'stickied'])

    def test_serialized_single_submission_should_have_expected_content(self):
        submission = self.rds.get_submission('7jgnxm')
        df = pd.read_csv(StringIO(self.rds._as_csv([submission])))
        self.assertEqual(df.iloc[0]['title'], 'Error with PRAW')
        self.assertEqual(df.iloc[0]['parent_id'], 't3_7jgnxm')
        self.assertEqual(df.iloc[0]['created_utc'], 1513140549.0)
        self.assertEqual(df.iloc[0]['is_submitter'], False)
