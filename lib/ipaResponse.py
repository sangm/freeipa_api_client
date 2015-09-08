class IPAResponse(object):
    """Describes what the freeIPA API returns"""
    def __init__(self, status_code, headers, expiration=None, session=None, failure=None):
        self.session = session
        self.status_code = status_code
        self.expiration = expiration
        self.headers = headers
        self.failure = failure
