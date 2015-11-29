from beanbag.v2 import BeanBag, POST, BeanBagException
import json
from nfsn.nfsnbeanbag import NfsnBeanBag
import pytest
import httpretty

class TestNfsnBeanbag(object):

    def setup(self):
        # Dummy endpoint, instead of 'https://api.nearlyfreespeech.net/'
        self.endpoint_url = 'https://api.example.net/'
        self.api_url = self.endpoint_url + 'dns/example.com/listRRs'

    def request_callback(self, request, uri, headers):
        payload = [
         {'data': '192.0.2.1',
          'name': '',
          'scope': 'member',
          'ttl': '3600',
          'type': 'A'},
         {'data': 'ns.phx2.nearlyfreespeech.net.',
          'name': '',
          'scope': 'member',
          'ttl': '3600',
          'type': 'NS'}]

        payload = {'jsondata':{'somekey': 'somevalue'}} # XXX not accurate
        headers['content-type'] = 'application/x-nfsn-api'
        return (200, headers, json.dumps(payload))

    @httpretty.activate
    def test_parse_fail_with_beanbag(self):
        """ An ordinary BeanBag object will fail because of the
        'application/x-nfsn-api' content-type header in the server's HTTP
        response. """
        nfsn = BeanBag(self.endpoint_url)

        httpretty.register_uri(
            httpretty.POST, self.api_url,
            body=self.request_callback)

        # When this test no longer raises a BeanBagException, it's possible
        # that the BeanBag authors might have updated their decoding function
        # to be more lax about handling non-application/json content-types. If
        # that's the case, this NfsnBeanBag wrapper class might become
        # unnecessary.
        with pytest.raises(BeanBagException):
            POST(nfsn.dns['example.com'].listRRs)

    @httpretty.activate
    def test_parse_with_nfsnbeanbag(self):
        """ The NfsnBeanBag class can handle the 'application/x-nfsn-api'
        content-type in the server's HTTP response. """

        nfsn = NfsnBeanBag(self.endpoint_url)

        httpretty.register_uri(
            httpretty.POST, self.api_url,
            body=self.request_callback)

        assert POST(nfsn.dns['example.com'].listRRs)
