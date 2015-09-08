import json
import requests
from ipaAuth import IPAAuth


class IPAClient(object):

    API_VERSION = '2.112'

    # TODO These two fields are temporary. Will encrypt/read from some other source when everything else is finished
    USERNAME = 'admin'
    PASSWORD = 'Secret123'

    def __init__(self, requests, baseUrl, sourceUrl, ipaAuth=None):
        self.requests = requests
        self.baseUrl = baseUrl
        self.sourceUrl = sourceUrl

        # this is done so that testing is easier
        if ipaAuth is None:
            self.ipaAuth = IPAAuth(requests=requests, baseUrl=baseUrl)
        else:
            self.ipaAuth = ipaAuth

        self.sessionExpiration = None
        self.sessionID = None

    def __getUrl__(self):
        return "%s/ipa/session/json" % self.baseUrl

    def __getHeader__(self, sessionID):
        return {
            'Content-Type': 'application/json',
            'Referer': '%s' % self.sourceUrl,
            'Accept': 'application/json',
            'Cookie': 'ipa_session=%s' % sessionID
        }

    def __getParams__(self, method, params, options=None):
        if options is None:
            options = {
                'version': self.API_VERSION
            }
        else:
            options['version'] = self.API_VERSION

        return {
            'method': method,
            'params': [
                params,
                options
            ]
        }

    def getLocalTime(self, timeZone):
        pass

    def sendRequest(self, method, params, options=None):
        if self.sessionID is None or not self.isSessionExpired(self.sessionExpiration, None):
            ipaResponse = self.ipaAuth.authenticate(self.USERNAME, self.PASSWORD)
            self.sessionID = ipaResponse.session
            self.sessionExpiration = ipaResponse.expiration

        url = self.__getUrl__()
        headers = self.__getHeader__(self.sessionID)
        params = self.__getParams__(method, params, options)

        response = requests.post(url, data=json.dumps(params), headers=headers, verify=False)
        try:
            return response.json()
        except ValueError:
            return response

    def isSessionExpired(self, sessionExpiration, localTime):
        # TODO Implement this, make sure both datetime objects are in the same timezone
        return False
