from mock import MagicMock
from lib import IPAAuth, IPAResponse, IPAClient
from tests import MockResponse
from dateutil.parser import parse
import unittest
import requests
import json
import os


class IPAClientTest(unittest.TestCase):
    def setUp(self):
        self.baseUrl = 'https://ipa.example.com'
        self.sourceUrl = 'https://gs.marcher.cs.txstate.edu'
        self.sessionID = 'b99a25695f578c0bb30cafb0932035bf'
        self.apiVersion = '2.112'
        self.ipaClient = IPAClient(requests=None,
                                   baseUrl=self.baseUrl,
                                   sourceUrl=self.sourceUrl,
                                   username='admin',
                                   password='Secret123')

    def testClient_getUrl(self):
        self.assertEquals('https://ipa.example.com/ipa/session/json', self.ipaClient.__getUrl__())

    def testClient_getHeaders(self):
        expectedHeader = {
            'Content-Type': 'application/json',
            'Referer': '%s' % self.sourceUrl,
            'Accept': 'application/json',
            'Cookie': 'ipa_session=%s' % self.sessionID
        }
        self.assertEquals(expectedHeader, self.ipaClient.__getHeader__(self.sessionID))

    def testClient_constructParams(self):
        expectedParams = {
            'method': 'user_find',
            'params': [
                ['user1', 'user2'],
                {'version': self.apiVersion}
            ]
        }

        self.assertEquals(expectedParams, self.ipaClient.__getParams__('user_find', ['user1', 'user2']))

    def testClient_constructParamsWithOptions(self):
        expectedParams = {
            'method': 'user_add',
            'params': [
                ['user1'],
                {
                    'version': self.apiVersion,
                    'sn': 'test',
                    'givenname': 'user'
                }
            ]
        }

        userOptions = {
            'sn': 'test',
            'givenname': 'user'
        }

        self.assertEquals(expectedParams, self.ipaClient.__getParams__('user_add', ['user1'], userOptions))

    def testClient_sendRequest(self):
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

        with open('%s/%s' % (os.path.dirname(__file__), 'resources/user_find_result.json')) as f:
            mockJson = json.load(f)
            mockResponse = MockResponse(
                status_code=200,
                headers=expectedHeaders,
                jsonValue=mockJson
            )

            expectedResultIPAResponse = IPAResponse(
                status_code=200,
                headers=expectedHeaders,
                raw_result=mockResponse,
                parsed_json=mockJson['result']['result'],
            )

            ipaAuth = IPAAuth(requests=None, baseUrl=self.baseUrl)
            ipaAuth.authenticate = MagicMock(return_value=expectedIPAResponse)

            requests.post = MagicMock(return_value=mockResponse)

            ipaClient = IPAClient(requests=requests,
                                  baseUrl=self.baseUrl,
                                  sourceUrl=self.sourceUrl,
                                  ipaAuth=ipaAuth)

            response = ipaClient.sendRequest('user_find', ['admin', 'register-marcher', 'smercado'])
            self.assertEquals(expectedResultIPAResponse.raw_result, response.raw_result)
            self.assertEquals(expectedResultIPAResponse.parsed_json, response.parsed_json)

    def testClient_sendRequest_noJsonValue(self):
        expectedIPAResponse = IPAResponse(
            session='b99a25695f578c0bb30cafb0932035bf',
            status_code=200,
            expiration='Sun, 06 Sep 2015 05:12:56 GMT',
            headers=None
        )

        mockResponse = MockResponse(
            status_code=500,
            headers=None
        )

        ipaAuth = IPAAuth(requests=None, baseUrl=self.baseUrl)
        ipaAuth.authenticate = MagicMock(return_value=expectedIPAResponse)
        requests.post = MagicMock(return_value=mockResponse)
        mockResponse.json = MagicMock(side_effect=ValueError('No JSON object could be decoded'))

        ipaClient = IPAClient(requests=requests,
                              baseUrl=self.baseUrl,
                              sourceUrl=self.sourceUrl,
                              ipaAuth=ipaAuth)

        result = ipaClient.sendRequest('user_find', ['admin', 'register-marcher', 'smercado'])
        self.assertEquals("No JSON object could be decoded", result.failure)


    def testClient_sessionExpiration_invalidType_returnsTrue(self):
        expiration = 'Sun, 06 Sep 2015 05:12:56 GMT'
        localTime = 'invalid'

        sessionExpired = self.ipaClient.isSessionExpired(expiration, localTime)
        self.assertTrue(sessionExpired)

    def testClient_sessionExpiration_notExpired_returnsFalse(self):
        expiration = 'Sun, 06 Sep 2015 05:12:56 GMT'
        localTime = parse('Sun, 06 Sep 2015 04:12:56 GMT')

        sessionExpired = self.ipaClient.isSessionExpired(expiration, localTime)
        self.assertFalse(sessionExpired)

    def testClient_sessionExpiration_expired_returnsTrue(self):
        expiration = 'Sun, 06 Sep 2015 11:12:56 GMT'
        localTime = parse('Sun, 06 Sep 2015 12:12:56 GMT')

        sessionExpired = self.ipaClient.isSessionExpired(expiration, localTime)
        self.assertTrue(sessionExpired)

    def testClient_sessionExpiration_invalidFormat(self):
        expiration = 'invalid'
        localTime = parse('Sun, 06 Sep 2015 06:12:56 GMT')

        sessionExpired = self.ipaClient.isSessionExpired(expiration, localTime)
        self.assertTrue(sessionExpired)

    def testClient_sessionExpiration_differentTimeZones(self):
        expiration = 'Sun, 06 Sep 2015 01:12:56 CST'  # 6:12:56 UTC
        localTime = parse('Sun, 06 Sep 2015 02:12:56 GMT')  # 2:12:56 UTC

        sessionExpired = self.ipaClient.isSessionExpired(expiration, localTime)
        self.assertFalse(sessionExpired)

if __name__ == '__main__':
    unittest.main()
