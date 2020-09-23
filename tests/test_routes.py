import unittest
from io import StringIO
import pandas as pd
from navcom_data_downloader import app, routes


class TestRoutes(unittest.TestCase):
    def setUp(self):
        with routes.app.test_client() as client:
            self.client = client

    def test_invalid_url_should_return_404(self):
        resp = self.client.get('/nothing_here_xxxx')
        self.assertEqual(resp.status_code, 404)

    def test_hello_should_return_hello_world(self):
        resp = self.client.get('/hello')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, b'Hello world.')

    def test_index_should_return_frontpage(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(b'<h1>Welcome</h1>' in resp.data)


class TestTwitterRoutes(unittest.TestCase):
    def setUp(self):
        with routes.app.test_client() as client:
            self.client = client

    def test_the_form_route_should_return_the_form(self):
        resp = self.client.get('/twitter')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(b'Please define your Twitter query.' in resp.data)
        self.assertTrue(b'<input id="string" type="text" name="string" required>' in resp.data)
        self.assertTrue(b'<button type="submit">Submit</button>' in resp.data)

    def test_submitted_form_should_return_response(self):
        query = "kittens"
        resp = self.client.post('/twitter-submit',
                                content_type='multipart/form-data',
                                data={'string': query},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_submitted_form_should_return_csv(self):
        query = "lama"
        resp = self.client.post('/twitter-submit',
                                content_type='multipart/form-data',
                                data={'string': query},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        mime_type, charset = [s.strip() for s in resp.headers['Content-Type'].split(';')]
        self.assertEqual(mime_type, 'text/csv')
        self.assertEqual(charset, 'charset=utf-8')
        disposition, filename = [s.strip() for s in resp.headers['content-disposition'].split(';')]
        self.assertEqual(disposition, 'attachment')
        self.assertEqual(filename, "filename=" + query + ".csv")


class TestRedditRoutes(unittest.TestCase):
    def setUp(self):
        app.logger.setLevel('INFO')
        with routes.app.test_client() as client:
            self.client = client

    def test_the_form_route_should_return_the_form(self):
        resp = self.client.get('/reddit')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(b'Please define your Reddit query.' in resp.data)
        self.assertTrue(b'<input id="submission-id" type="text" name="submission_id" required>' in resp.data)
        self.assertTrue(b'<input id="subreddit" type="text" name="subreddit" required>' in resp.data)
        self.assertTrue(b'<select name="kind" id="kind" required>' in resp.data)
        self.assertTrue(b'<button type="submit">Submit</button>' in resp.data)

    def test_submitted_empty_submission_form_should_fail(self):
        with self.assertRaises(KeyError) as cm:
            resp = self.client.post('/reddit-submission-submit',
                                    content_type='multipart/form-data',
                                    data={},
                                    follow_redirects=True)

    def test_submitted_submission_form_should_get_the_submission(self):
        resp = self.client.post('/reddit-submission-submit',
                                content_type='multipart/form-data',
                                data={'submission_id':  '7jgnxm'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(b'Error with PRAW' in resp.data)

    def test_submitted_empty_subreddit_form_should_fail(self):
        with self.assertRaises(KeyError) as cm:
            resp = self.client.post('/reddit-subreddit-submit',
                                    content_type='multipart/form-data',
                                    data={},
                                    follow_redirects=True)
            self.assertEqual(resp.status_code, 400)

    def test_submitted_subreddit_form_missing_subreddit_should_fail(self):
        with self.assertRaises(KeyError) as cm:
            kind = 'kind'
            resp = self.client.post('/reddit-subreddit-submit',
                                    content_type='multipart/form-data',
                                    data={'kind': kind},
                                    follow_redirects=True)
            self.assertEqual(resp.status_code, 400)

    def test_submitted_subreddit_form_missing_kind_should_fail(self):
        with self.assertRaises(KeyError) as cm:
            subreddit = "dataisbeautiful"
            resp = self.client.post('/reddit-subreddit-submit',
                                    content_type='multipart/form-data',
                                    data={'subreddit': subreddit},
                                    follow_redirects=True)
            self.assertEqual(resp.status_code, 400)

    def test_submitted_subreddit_form_with_weird_kind_should_fail(self):
        with self.assertRaises(KeyError) as cm:
            subreddit = "dataisbeautiful"
            kind = 'horse'
            resp = self.client.post('/reddit-subreddit-submit',
                                    content_type='multipart/form-data',
                                    data={'subreddit': subreddit, 'kind': kind},
                                    follow_redirects=True)
            self.assertEqual(resp.status_code, 400)

    def test_submitted_subreddit_form_with_very_weird_kind_should_fail(self):
        with self.assertRaises(KeyError) as cm:
            subreddit = "dataisbeautiful"
            kind = ['horse', 42]
            resp = self.client.post('/reddit-subreddit-submit',
                                    content_type='multipart/form-data',
                                    data={'subreddit': subreddit, 'kind': kind},
                                    follow_redirects=True)
            self.assertEqual(resp.status_code, 400)

    def test_submitted_subreddit_form_with_hot_kind_should_return(self):
        subreddit = "dataisbeautiful"
        kind = 'hot'
        resp = self.client.post('/reddit-subreddit-submit',
                                content_type='multipart/form-data',
                                data={'subreddit': subreddit, 'kind': kind},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_submitted_subreddit_form_with_new_kind_should_return(self):
        subreddit = "dataisbeautiful"
        kind = 'new'
        resp = self.client.post('/reddit-subreddit-submit',
                                content_type='multipart/form-data',
                                data={'subreddit': subreddit, 'kind': kind},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_submitted_subreddit_form_with_top_kind_should_return(self):
        with self.assertRaises(NotImplementedError) as cm:
            subreddit = "dataisbeautiful"
            kind = 'top'
            resp = self.client.post('/reddit-subreddit-submit',
                                    content_type='multipart/form-data',
                                    data={'subreddit': subreddit, 'kind': kind},
                                    follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

    def test_submitted_subreddit_form_should_return_response(self):
        subreddit = "dataisbeautiful"
        kind = 'hot'
        resp = self.client.post('/reddit-subreddit-submit',
                                content_type='multipart/form-data',
                                data={'subreddit': subreddit, 'kind': kind},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_submitted_subreddit_form_should_return_csv(self):
        subreddit = "dataisbeautiful"
        kind = 'hot'
        resp = self.client.post('/reddit-subreddit-submit',
                                content_type='multipart/form-data',
                                data={'subreddit': subreddit, 'kind': kind},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        mime_type, charset = [s.strip() for s in resp.headers['Content-Type'].split(';')]
        self.assertEqual(mime_type, 'text/csv')
        self.assertEqual(charset, 'charset=utf-8')
        disposition, filename = [s.strip() for s in resp.headers['content-disposition'].split(';')]
        self.assertEqual(disposition, 'attachment')
        self.assertEqual(filename, "filename=" + subreddit + '-' + kind + ".csv")

    def test_submitted_subreddit_form_should_return_parseable_csv(self):
        subreddit = "dataisbeautiful"
        kind = 'hot'
        resp = self.client.post('/reddit-subreddit-submit',
                                content_type='multipart/form-data',
                                data={'subreddit': subreddit, 'kind': kind},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        df = pd.read_csv(StringIO(str(resp.data)))
        self.assertIsInstance(df, pd.DataFrame)
