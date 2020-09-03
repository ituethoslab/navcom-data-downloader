from navcom_data_downloader import app

class DataSource():
    def __init__(self):
        app.logger.debug(f"Generic DataSource instantiated")

    def query(self, query):
        app.logger.debug("Would query for '{query}'")
        ...


class TwitterDataSource(DataSource):
    def __init__(self):
        super().__init__()

    def query(self, query):
        app.logger.debug(f"Would search Twitter for '{query}'")
        return query
