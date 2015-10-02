import urllib
from Cookie import SimpleCookie
from ipaResponse import IPAResponse


class IPAAuth(object):
    """Class responsible for calling FreeIPA's json api"""

    KEY_USER = 'user'
    KEY_PASSWORD = 'password'

    def __init__(self, requests, baseUrl):
        """
        :param requests: requests object to call freeipa web api
        :param baseUrl: base url for the FQDN (fully qualified domain name)
        """
        self.baseUrl = baseUrl
        self.requests = requests
        self.ipaResponse = None

    def __getUrl__(self):
        return "%s/ipa/session/login_password" % self.baseUrl

    def __getHeader__(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
        }

    def __urlEncodeUserData__(self, userData):
        """
        :param data: a dictionary describing user's login name and password
        :return: url encoded string
        """

        if self.KEY_USER not in userData or self.KEY_PASSWORD not in userData:
            raise ValueError('Missing user/password key')

        return urllib.urlencode(userData)

    def authenticate(self, username, password):
        """
        :param username:
        :param password:
        :return: IPAResponse
        """

        # kinit is case sensitive, so we have to lowercase username given to data field
        userData = {
            self.KEY_USER: username.lower(),
            self.KEY_PASSWORD: password
        }

        response = self.requests.post(self.__getUrl__(),
                                      data=self.__urlEncodeUserData__(userData),
                                      verify=False,
                                      headers=self.__getHeader__())

        if response.status_code == 200:
            cookie = SimpleCookie(response.headers['set-cookie'])
            return IPAResponse(
                session=cookie['ipa_session'].value,
                status_code=response.status_code,
                expiration=cookie['ipa_session']['expires'],
                headers=response.headers
            )
        elif response.status_code == 401:
            # authorization failure
            return IPAResponse(
                status_code=response.status_code,
                headers=response.headers,
                failure=response.headers['x-ipa-rejection-reason']
            )
        else:
            # this shouldn't happen; let's log this to a dedicated file somewhere
            return IPAResponse(
                status_code=response.status_code,
                headers=response.headers,
                failure=response
            )
