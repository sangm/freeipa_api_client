from mock import MagicMock
from lib.ipaAuth import IPAAuth, IPAResponse
from lib.ipaClient import IPAClient
from tests.MockResponse import MockResponse
import unittest
import requests
import json
import os

class ipaClientTest(unittest.TestCase):
    def setUp(self):
        self.baseUrl = 'https://ipa.example.com'
        self.sourceUrl = 'https://gs.marcher.cs.txstate.edu'
        self.sessionID = 'b99a25695f578c0bb30cafb0932035bf'
        self.apiVersion = '2.112'
        self.ipaClient = IPAClient(requests=None, baseUrl=self.baseUrl, sourceUrl=self.sourceUrl)

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

        with open('%s/%s' % (os.path.dirname(__file__),'resources/user_find_result.json')) as f:
            mockJson = json.load(f)
            mockResponse = MockResponse(
                status_code=200,
                headers=expectedHeaders,
                jsonValue=mockJson
            )

            ipaAuth = IPAAuth(requests=None, baseUrl=self.baseUrl)
            ipaAuth.authenticate = MagicMock(return_value=expectedIPAResponse)

            requests.post = MagicMock(return_value=mockResponse)

            ipaClient = IPAClient(requests=requests,
                                  baseUrl=self.baseUrl,
                                  sourceUrl=self.sourceUrl,
                                  ipaAuth=ipaAuth)

            result = ipaClient.sendRequest('user_find', ['admin', 'register-marcher', 'smercado'])

            self.assertEquals(3, result['result']['count'])

if __name__ == '__main__':
    unittest.main()