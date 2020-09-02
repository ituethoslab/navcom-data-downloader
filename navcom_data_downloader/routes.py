from navcom_data_downloader import app

@app.route('/hello')
def hello_world():
    return "Hello world."
