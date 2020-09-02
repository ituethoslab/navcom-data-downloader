from navcom_data_downloader import app

@app.route('/hello')
def hello_world():
    app.logger.debug("Hello world route was requested.")
    return "Hello world."
