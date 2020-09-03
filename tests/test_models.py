import unittest
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
        data = tds.query(query)
        self.assertEqual(10, len(data))

    def test_querying_with_no_params_should_raise_an_error(self):
        query = {}
        tds = TwitterDataSource()
        with self.assertRaises(KeyError):
            data = tds.query(query)

    def test_query_with_only_string_should_be_sufficient(self):
        query = {'string': 'goats'}
        tds = TwitterDataSource()
        data = tds.query(query)
        self.assertEqual(10, len(data))
