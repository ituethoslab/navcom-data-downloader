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
    resp.headers["content-disposition"] = "attachment; filename=" + request.form['string'] + '.csv' # "data.csv"
    return resp

@app.route('/reddit')
def reddit():
    app.logger.debug("Route %s", "/reddit")
    return render_template('reddit.html')

@app.route('/reddit-submit', methods=['POST'])
def reddit_submit():
    app.logger.debug("Route %s, payload %s", "/reddit-submit", request.form)
    rds = RedditDataSource()
    data = None
    if request.form['kind'] == 'hot':
        data = rds.get_hot(request.form['subreddit'])
    elif request.form['kind'] == 'new':
        data = rds.get_new(request.form['subreddit'])
    elif request.form['kind'] == 'top':
        data = rds.get_top(request.form['subreddit'])

    resp = app.make_response(data)
    resp.mimetype = 'text/csv'
    filename = request.form['subreddit'] + '-' + request.form['kind'] + '.csv'
    resp.headers["content-disposition"] = "attachment; filename=" + filename

    return resp

@app.route('/reddit-hot-dataisbeautiful')
def reddit_hot_dataisbeautiful():
    app.logger.debug("Route %s", "/reddit-hot-dataisbeautiful")
    rds = RedditDataSource()
    submissions = rds.get_hot('dataisbeautiful', limit=5)
    return submissions

