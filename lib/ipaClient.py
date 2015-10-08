import json
import requests
import datetime
import pytz
from ipaAuth import IPAAuth
from dateutil.parser import parse


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

        self.timeZone = pytz.timezone('US/Pacific')

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

    def sendRequest(self, method, params, options=None):
        """
        sends the request to json api using requests library
        :param method:
        :param params:
        :param options:
        :return:
        """
        if self.sessionID is None \
                or self.sessionExpiration is None \
                or self.isSessionExpired(self.sessionExpiration, self.__getLocalTime__()):
            ipaResponse = self.ipaAuth.authenticate(self.USERNAME, self.PASSWORD)
            self.sessionID = ipaResponse.session
            self.sessionExpiration = ipaResponse.expiration

        url = self.__getUrl__()
        headers = self.__getHeader__(self.sessionID)
        params = self.__getParams__(method, params, options)

        return requests.post(url, data=json.dumps(params), headers=headers, verify=False)

    def __getLocalTime__(self):
        """
        handle everything utc timezone
        """
        return datetime.now(pytz.utc)

    def isSessionExpired(self, sessionExpiration, localTimeDate):
        """
        :param sessionExpiration: date string from freeipa api
        :param localTimeDate: local time of system
        :return: whether or not session is expired
        """
        if not isinstance(localTimeDate, datetime.date):
            return True

        try:
            sessionExpirationDate = parse(sessionExpiration)
        except ValueError:
            return True

        # the api returns datetime with tzinfo. If not set, let's assume the data is invalid
        if not sessionExpirationDate.tzinfo or not localTimeDate.tzinfo:
            return True

        # normalize both date time objects to utc
        sessionExpirationDate = sessionExpirationDate.astimezone(pytz.utc)
        localTimeDate = localTimeDate.astimezone(pytz.UTC)

        return sessionExpirationDate < localTimeDate
