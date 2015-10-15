class IPAResponse(object):
    """Describes what the freeIPA API returned"""
    def __init__(self, status_code, headers, expiration=None, session=None, failure=None,
                 raw_result=None, parsed_json=None):
        self.session = session
        self.status_code = status_code
        self.expiration = expiration
        self.headers = headers
        self.failure = failure
        self.raw_result = raw_result
        self.parsed_json = parsed_json
