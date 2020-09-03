from navcom_data_downloader import app
from navcom_data_downloader.models import TwitterDataSource
from flask import render_template, request

@app.route('/hello')
def hello_world():
    app.logger.debug("Hello world route was requested.")
    return "Hello world."

@app.route('/')
def index():
    app.logger.debug("Route %s", "/")
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    app.logger.debug("Route %s, payload %s", "/submit", request.form)
    ds = TwitterDataSource()
    ds_resp = ds.query(request.form)
    return "\n".join([r.text for r in ds_resp])
