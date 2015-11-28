from nfsn.auth import NfsnAuth
import requests
import string
import time

class TestNfsnAuth(object):

    def setup(self):
        self.auth = NfsnAuth('testlogin', 'testapikey123')

    def test_salt_length(self):
        """ salt must be 16 characters """
        assert len(self.auth._salt()) == 16

    def test_salt_is_unique(self):
        s1 = self.auth._salt()
        s2 = self.auth._salt()
        assert s1 != s2

    def test_salt_characters(self):
        """ salt must be alphanumeric """
        salt_characters = string.ascii_letters + string.digits
        for c in self.auth._salt():
            assert c in salt_characters

    def test_timestamp(self, monkeypatch):
        """ Check that timestamp uses time.time """
        monkeypatch.setattr(time, 'time', lambda: 1000000)
        assert self.auth._timestamp() == '1000000'

    def test_header(self, monkeypatch):
        """ Check that X-NFSN-Authentication is set """
        monkeypatch.setattr(time, 'time', lambda: '1000000')
        monkeypatch.setattr(self.auth, '_salt', lambda: 'yumsalty1234')
        url = 'https://api.nearlyfreespeech.net/testing'
        r = requests.Request('GET', url, data='')
        expected = 'testlogin;1000000;yumsalty1234;d20e2ee4105b82060f4c0ea9c2d9a91a3b6cdd13'
        r_authenticated = self.auth(r.prepare())
        assert r_authenticated.headers['X-NFSN-Authentication'] == expected
