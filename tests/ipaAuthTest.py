from tests import MockResponse
from mock import MagicMock, ANY
from lib import IPAAuth, IPAResponse
import unittest
import requests


class IPAAuthTest(unittest.TestCase):
    def setUp(self):
        self.baseUrl = 'https://ipa.example.com'
        self.ipaAuth = IPAAuth(requests=None, baseUrl=self.baseUrl)

    def testAuth_getUrl(self):
        self.assertEquals('https://ipa.example.com/ipa/session/login_password', self.ipaAuth.__getUrl__())

    def testAuth_getHeaders(self):
        # expected http header
        expectedHeader = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
        }
        self.assertEquals(expectedHeader, self.ipaAuth.__getHeader__())

    def testAuth_getUserAuthData_throwsExceptionMissingUserKey(self):
        with self.assertRaises(ValueError):
            self.ipaAuth.__urlEncodeUserData__({'password': 'password'})

        with self.assertRaises(ValueError):
            self.ipaAuth.__urlEncodeUserData__({'user': 'admin'})

    def testAuth_getData(self):
        self.assertEquals('password=password&user=admin', self.ipaAuth.__urlEncodeUserData__({
            'user': 'admin',
            'password': 'password'
        }))

    def testAuth_sendAuthRequest_success(self):
        expectedHeaders = {
            'content-length': '0',
            'set-cookie': 'ipa_session=b99a25695f578c0bb30cafb0932035bf; Domain=ipa.example.test; Path=/ipa; Expires=Sun, 06 Sep 2015 05:12:56 GMT; Secure; HttpOnly',
            'keep-alive': 'timeout=5, max=100',
            'server': 'Apache/2.4.6 (CentOS) mod_auth_kerb/5.4 mod_nss/2.4.6 NSS/3.16.2.3 Basic ECC mod_wsgi/3.4 Python/2.7.5',
            'connection': 'Keep-Alive',
            'date': 'Sun, 06 Sep 2015 04:52:56 GMT',
            'content-type': 'text/plain; charset=UTF-8'
        }

        expectedIPAResponse = IPAResponse(
            session='b99a25695f578c0bb30cafb0932035bf',
            status_code=200,
            expiration='Sun, 06 Sep 2015 05:12:56 GMT',
            headers=expectedHeaders
        )

        requestResponseObject = MockResponse(
            headers=expectedHeaders,
            status_code=200
        )

        requests.post = MagicMock(return_value=requestResponseObject)


        ipaClient = IPAAuth(requests=requests, baseUrl=self.baseUrl)

        result = ipaClient.authenticate(
            username='admin',
            password='password'
        )

        self.assertEquals(expectedIPAResponse.session, result.session)
        self.assertEquals(expectedIPAResponse.headers, result.headers)
        self.assertEquals(expectedIPAResponse.status_code, result.status_code)
        self.assertEquals(expectedIPAResponse.expiration, result.expiration)

    def testAuth_sendAuthRequest_fail(self):
        expectedHeaders = {
            'content-length': '201',
            'keep-alive': 'timeout=5, max=100',
            'server': 'Apache/2.4.6 (CentOS) mod_auth_kerb/5.4 mod_nss/2.4.6 NSS/3.16.2.3 Basic ECC mod_wsgi/3.4 Python/2.7.5',
            'x-ipa-rejection-reason': 'invalid-password',
            'connection': 'Keep-Alive',
            'date': 'Sun, 06 Sep 2015 07:49:28 GMT',
            'content-type': 'text/html; charset=utf-8'
        }

        expectedIPAResponse = IPAResponse(
            status_code=401,
            headers=expectedHeaders,
            failure='invalid-password'
        )

        requestResponseObject = MockResponse(
            headers=expectedHeaders,
            status_code=401
        )
        requests.post = MagicMock(return_value=requestResponseObject)

        ipaClient = IPAAuth(requests=requests, baseUrl=self.baseUrl)

        result = ipaClient.authenticate(
            username='non-existing-user',
            password='does not matter'
        )

        self.assertEquals(expectedIPAResponse.session, result.session)
        self.assertEquals(expectedIPAResponse.headers, result.headers)
        self.assertEquals(expectedIPAResponse.status_code, result.status_code)
        self.assertEquals(expectedIPAResponse.expiration, result.expiration)

    def testAuth_sendAuthRequest_invalid(self):
        expectedIPAResponse = IPAResponse(
            status_code=999,
            headers=None,
            failure='graceful failure for status codes that is not 200 or 401'
        )
        requestResponseObject = MockResponse(
            headers=None,
            status_code=999
        )
        requests.post = MagicMock(return_value=requestResponseObject)
        ipaClient = IPAAuth(requests=requests, baseUrl=self.baseUrl)

        result = ipaClient.authenticate('fff', 'fab')

        # The function returns the entire response so that it will be easier to debug
        self.assertEquals(requestResponseObject, result.failure)


    def testAuth_getData_caseSensitivity(self):
        # kinit is case sensitive, so we have to lowercase all the params given to data field
        requests.post = MagicMock()

        ipaClient = IPAAuth(requests=requests, baseUrl=self.baseUrl)

        ipaClient.authenticate('testUser', 'passWord')

        (arg, kwargs) = requests.post.call_args

        self.assertEquals('password=passWord&user=testuser', kwargs['data'])



if __name__ == '__main__':
    unittest.main()
