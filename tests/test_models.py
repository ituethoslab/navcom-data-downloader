import unittest
import datetime
import praw
import pandas as pd
from io import StringIO
from config import RedditCredentials, RedditConfig
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


class TestRedditCredentials(unittest.TestCase):
    def setUp(self):
        self.reddit_conf = RedditCredentials

    def test_credentials_should_incluce_all_the_necessary_keys(self):
        self.assertIn('client_id', dir(self.reddit_conf))
        self.assertIn('client_secret', dir(self.reddit_conf))
        self.assertIn('username', dir(self.reddit_conf))
        self.assertIn('password', dir(self.reddit_conf))
        self.assertIn('user_agent', dir(self.reddit_conf))

    def test_credentials_should_have_some_values(self):
        self.assertIsInstance(self.reddit_conf.client_id, str)
        self.assertIsInstance(self.reddit_conf.client_secret, str)
        self.assertIsInstance(self.reddit_conf.username, str)
        self.assertIsInstance(self.reddit_conf.password, str)
        self.assertIsInstance(self.reddit_conf.user_agent, str)


class TestRedditDataSource(unittest.TestCase):
    def setUp(self):
        # app.logger.setLevel('INFO')
        self.rds = RedditDataSource()

    def test_instantiating_should_be_fine(self):
        self.assertIsInstance(self.rds, RedditDataSource)
        self.assertIsInstance(self.rds.reddit, praw.reddit.Reddit)

    def test_authentication_should_succeed(self):
        ...

    # Test the private retrieving method.
    def test_getting_a_specific_submission_by_id_should_succeed(self):
        sid = '7jgnxm'
        submission = self.rds._get_submission(sid)
        self.assertEqual(submission.id, sid)

    def test_getting_hot_from_a_subreddit_should_succeed(self):
        subreddit = 'dataisbeautiful'
        submissions = self.rds._query(subreddit, 'hot')
        self.assertTrue(all([submission.subreddit.display_name == subreddit for submission in submissions]))

    def test_getting_hot_from_a_subreddit_wo_limit_should_get_configured_number_of_results(self):
        """This takes time."""
        subreddit = 'dataisbeautiful'
        submissions = self.rds._query(subreddit, 'hot')
        self.assertEqual(len(submissions), RedditConfig.limit)

    def test_getting_hot_from_a_subreddit_with_limit_should_limit_the_number_of_results(self):
        subreddit = 'dataisbeautiful'
        few_submissions = self.rds._query(subreddit, 'hot', limit=3)
        self.assertLessEqual(len(few_submissions), 3)

    def test_getting_hot_from_a_subreddit_with_increased_limit_should_increase_number_of_results(self):
        subreddit = 'dataisbeautiful'
        more_submissions = self.rds._query(subreddit, 'hot', RedditConfig.limit + 5)
        self.assertEqual(len(more_submissions), RedditConfig.limit + 5)

    # Test serialization.
    def test_serializing_a_single_submission_should_work(self):
        submission = self.rds._get_submission('7jgnxm')
        self.assertIsInstance(self.rds._as_csv([submission]), str)
        self.assertEqual(len(self.rds._as_csv([submission])), 542)

    def test_serialized_single_submission_should_parse_with_pandas(self):
        submission = self.rds._get_submission('7jgnxm')
        df = pd.read_csv(StringIO(self.rds._as_csv([submission])))
        self.assertEqual(df.shape, (1, 9))

    def test_serialized_single_submission_should_have_expected_header(self):
        submission = self.rds._get_submission('7jgnxm')
        df = pd.read_csv(StringIO(self.rds._as_csv([submission])))
        self.assertEqual(list(df.columns), ['header', 'comments', 'author', 'created_utc', 'edited', 'score', 'is_submitter', 'parent_id', 'stickied'])

    def test_serialized_single_submission_should_have_expected_content(self):
        submission = self.rds._get_submission('7jgnxm')
        df = pd.read_csv(StringIO(self.rds._as_csv([submission])))
        self.assertEqual(df.iloc[0]['header'], 'Error with PRAW')
        self.assertEqual(df.iloc[0]['parent_id'], 't3_7jgnxm')
        self.assertEqual(df.iloc[0]['created_utc'], 1513140549.0)
        self.assertEqual(df.iloc[0]['is_submitter'], False)

    def test_serialized_entries_should_be_free_of_newlines(self):
        submissions = self.rds.get_hot('dataisbeautiful', limit=50)
        df = pd.read_csv(StringIO(submissions))
        self.assertFalse(any(df['comments'].dropna().str.match('\n')))

    # Test public methods which return serialized CSV.
    def test_getting_a_specific_submission_by_id_should_return_csv(self):
        sid = '7jgnxm'
        submission = self.rds.get_submission(sid)
        self.assertIsInstance(submission, str)
        self.assertEqual(542, len(submission))
        df = pd.read_csv(StringIO(submission))
        self.assertEqual(df.iloc[0]['header'], "Error with PRAW")

    def test_getting_hot_from_a_subreddit_should_return_csv(self):
        subreddit = 'dataisbeautiful'
        submissions = self.rds.get_hot(subreddit, limit=3)
        self.assertIsInstance(submissions, str)
        df = pd.read_csv(StringIO(submissions))
        self.assertLessEqual(len(df['header'].unique()), 3, "How many submissions are these comments from?")
        self.assertEqual(len(df.columns), 9)

    def test_getting_new_from_a_subreddit_should_return_csv(self):
        subreddit = 'dataisbeautiful'
        submissions = self.rds.get_new(subreddit, limit=5)
        self.assertIsInstance(submissions, str)
        df = pd.read_csv(StringIO(submissions))
        self.assertLessEqual(len(df['header'].unique()), 5, "How many submissions are these comments from?")
        self.assertEqual(len(df.columns), 9)
