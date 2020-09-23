from navcom_data_downloader import app
from navcom_data_downloader.models import TwitterDataSource, RedditDataSource
from flask import render_template, request, Response

@app.route('/hello')
def hello_world():
    app.logger.debug("Hello world route was requested.")
    return "Hello world."

@app.route('/')
def index():
    app.logger.debug("Route %s", "/")
    return render_template('index.html')

@app.route('/twitter')
def twitter():
    app.logger.debug("Route %s", "/twitter")
    return render_template('twitter.html')

@app.route('/twitter-submit', methods=['POST'])
def twitter_submit():
    app.logger.debug("Route %s, payload %s", "/twitter-submit", request.form)
    ds = TwitterDataSource()
    ds_resp = ds.query(request.form)

    resp = app.make_response(ds_resp)
    resp.mimetype = 'text/csv'
    resp.headers["content-disposition"] = "attachment; filename=" + request.form['string'] + '.csv'

    return resp

@app.route('/reddit')
def reddit():
    app.logger.debug("Route %s", "/reddit")
    return render_template('reddit.html')

@app.route('/reddit-submission-submit', methods=['POST'])
def reddit_submission_submit():
    app.logger.debug("Route %s, payload %s", "/reddit-submission-submit", request.form)
    rds = RedditDataSource()
    submission = rds.get_submission(request.form['submission_id'])

    resp = app.make_response(submission)
    resp.mimetype = 'text/csv'
    resp.headers["content-disposition"] = "attachment; filename=" + request.form['submission_id'] + '.csv'

    return resp

@app.route('/reddit-subreddit-submit', methods=['POST'])
def reddit_subreddit_submit():
    app.logger.debug("Route %s, payload %s", "/reddit-subreddit-submit", request.form)
    rds = RedditDataSource()
    data = None
    if request.form['kind'] == 'hot':
        data = rds.get_hot(request.form['subreddit'])
    elif request.form['kind'] == 'new':
        data = rds.get_new(request.form['subreddit'])
    elif request.form['kind'] == 'top':
        data = rds.get_top(request.form['subreddit'])
    else:
        raise KeyError

    resp = app.make_response(data)
    resp.mimetype = 'text/csv'
    filename = request.form['subreddit'] + '-' + request.form['kind'] + '.csv'
    resp.headers["content-disposition"] = "attachment; filename=" + filename

    return resp
