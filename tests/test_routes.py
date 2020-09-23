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


class TestTwitterRoutes(unittest.TestCase):
    def setUp(self):
        with routes.app.test_client() as client:
            self.client = client

    def test_submitted_form_should_return_response(self):
        query = "kittens"
        resp = self.client.post('/twitter-submit',
                                content_type='multipart/form-data',
                                data={'string': query},
                                follow_redirects=True)
        self.assertEqual(200, resp.status_code)

    def test_submitted_form_should_returns_csv(self):
        query = "lama"
        resp = self.client.post('/twitter-submit',
                                content_type='multipart/form-data',
                                data={'string': query},
                                follow_redirects=True)
        self.assertEqual(200, resp.status_code)
        mime_type, charset = [s.strip() for s in resp.headers['Content-Type'].split(';')]
        self.assertEqual(mime_type, 'text/csv')
        self.assertEqual(charset, 'charset=utf-8')
        disposition, filename = [s.strip() for s in resp.headers['content-disposition'].split(';')]
        self.assertEqual(disposition, 'attachment')
        self.assertEqual(filename, "filename=" + query + ".csv")
