import unittest
from navcom_data_downloader import routes

class TestRoutes(unittest.TestCase):
    def setUp(self):
        with routes.app.test_client() as client:
            self.client = client

    def test_invalid_url_should_return_404(self):
        resp = self.client.get('/nothing_here_xxxx')
        self.assertEqual(404, resp.status_code)

    def test_hello_should_return_hello_world(self):
        resp = self.client.get('/hello')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(b'Hello world.', resp.data)

    def test_submitted_form_should_contain_query_string(self):
        query = "kittens"
        resp = self.client.post('/submit',
                                # content_type='multipart/form-data',
                                data={'query': query},
                                follow_redirects=True)
        self.assertEqual(200, resp.status_code)
        self.assertIn(bytes(query, encoding='utf-8'), uresp.data)
