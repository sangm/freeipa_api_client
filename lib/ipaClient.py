import json
import requests
from ipaAuth import IPAAuth


class IPAClient(object):
    """Class is responsible for sending commands to FreeIPA's JSON API."""

    API_VERSION = '2.112'

    def __init__(self, requests, baseUrl, sourceUrl, ipaAuth=None, username=None, password=None):
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

        self.USERNAME = username
        self.PASSWORD = password

    def __getUrl__(self):
        """
        :return: api end point to send commands to.
        """
        return "%s/ipa/session/json" % self.baseUrl

    def __getHeader__(self, sessionID):
        """
        :param sessionID: cookie from authentication end point.
        :return: minimum HTTP header needed for json api.
        """
        return {
            'Content-Type': 'application/json',
            'Referer': '%s' % self.sourceUrl,
            'Accept': 'application/json',
            'Cookie': 'ipa_session=%s' % sessionID
        }

    def __getParams__(self, method, params, options=None):
        """
        JSON api takes an array of parameters and a json object for options, we are constructing that here.

        :param method:
        :param params:
        :param options:
        :return: parameter object
        """
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
        """
        sends the request to json api using requests library
        :param method:
        :param params:
        :param options:
        :return:
        """
        if self.sessionID is None or not self.isSessionExpired(self.sessionExpiration, None):
            ipaResponse = self.ipaAuth.authenticate(self.USERNAME, self.PASSWORD)
            self.sessionID = ipaResponse.session
            self.sessionExpiration = ipaResponse.expiration

        url = self.__getUrl__()
        headers = self.__getHeader__(self.sessionID)
        params = self.__getParams__(method, params, options)

        return requests.post(url, data=json.dumps(params), headers=headers, verify=False)

    def isSessionExpired(self, sessionExpiration, localTime):
        # TODO Implement this, make sure both datetime objects are in the same timezone
        return False
