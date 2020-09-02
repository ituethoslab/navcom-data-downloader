from navcom_data_downloader import app
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
    app.logger.debug("Route %s", "/submit")
    return "Imagine data here"
