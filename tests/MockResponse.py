class MockResponse(object):
    def __init__(self, headers, status_code, jsonValue=None):
        self.headers = headers
        self.status_code = status_code
        self.jsonValue = jsonValue

    def json(self):
        return self.jsonValue