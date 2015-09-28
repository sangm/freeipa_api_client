import urllib


class IPAPassword(object):
    """Class responsible for calling FreeIPA's json api"""

    KEY_USER = 'user'
    KEY_OLD_PASSWORD = 'old_password'
    KEY_NEW_PASSWORD = 'new_password'
    MSG_MISSING_KEYS = 'Missing one or more of the following keys [%s, %s, %s]' % (KEY_USER,
                                                                                   KEY_NEW_PASSWORD,
                                                                                   KEY_OLD_PASSWORD)

    def __init__(self, requests, baseUrl):
        """
        :param requests: requests object to call freeipa web api
        :param baseUrl: base url for the FQDN (fully qualified domain name)
        """
        self.baseUrl = baseUrl
        self.requests = requests
        self.ipaResponse = None

    def __getUrl__(self):
        return "%s/ipa/session/change_password" % self.baseUrl

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

        if self.KEY_USER not in userData or self.KEY_OLD_PASSWORD not in userData or self.KEY_NEW_PASSWORD not in \
                userData:
            raise ValueError(self.MSG_MISSING_KEYS)

        return urllib.urlencode(userData)

    def changePassword(self, username, oldPassword, newPassword):
        userData = {
            self.KEY_USER: username,
            self.KEY_OLD_PASSWORD: oldPassword,
            self.KEY_NEW_PASSWORD: newPassword
        }

        response = self.requests.post(self.__getUrl__(),
                                      data=self.__urlEncodeUserData__(userData),
                                      verify=False,
                                      headers=self.__getHeader__())

        responseHeaders = response.headers

        return responseHeaders['x-ipa-pwchange-result'] == 'ok'
