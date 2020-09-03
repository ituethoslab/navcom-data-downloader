import unittest
import datetime
from navcom_data_downloader.models import DataSource, TwitterDataSource

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
