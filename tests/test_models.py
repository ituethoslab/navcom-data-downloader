import unittest
from navcom_data_downloader.models import DataSource, TwitterDataSource

class TestDataSource(unittest.TestCase):
    def test_instantiating_generic_model_should_be_fine(self):
        ds = DataSource()
        self.assertIsInstance(ds, DataSource)


class TestTwitterDataSource(unittest.TestCase):
    def test_instantiating_twitter_model_should_be_fine(self):
        tds = TwitterDataSource()
        self.assertIsInstance(tds, TwitterDataSource)
    
    def test_querying_twitter_model_should_log_params(self):
        query = "giraffe"
        tds = TwitterDataSource()
        self.assertEqual(query, tds.query(query))
