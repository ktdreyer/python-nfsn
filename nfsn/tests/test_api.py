from nfsn import Nfsn
import httpretty
import os
import pytest
import re
from shutil import copyfile
try:
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

tests_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_dir = os.path.join(tests_dir, 'fixtures')

def setup_module(module):
    API_ENDPOINT = 'https://api.nearlyfreespeech.net/'

    url_regex = re.compile(API_ENDPOINT + '.*')
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, url_regex,
        body=get_request_callback)
    httpretty.register_uri(
        httpretty.POST, url_regex,
        body=post_request_callback)
    httpretty.register_uri(
        httpretty.PUT, url_regex,
        body=put_request_callback)

def get_request_callback(request, uri, headers):
    # The response bodies are stored in flat files under the
    # "fixtures/payloads" directory (fixtures_dir).
    # E.g. tests/fixtures/payloads/dns/example.com/listRRs
    request_path = urlparse(uri).path
    payload_file = fixtures_dir + '/responses/' + request_path

    with open(payload_file) as data_file:
         payload = data_file.read()

    headers['content-type'] = 'application/x-nfsn-api'
    return (200, headers, payload)

def post_request_callback(request, uri, headers):
    return get_request_callback(request, uri, headers)

def put_request_callback(request, uri, headers):
    headers['content-type'] = 'application/x-nfsn-api'
    return (200, headers, request.body)


class NfsnTest(object):

    nfsn = Nfsn(login='guest', api_key='1234567890123456')

    #def teardown(self):
    #    httpretty.disable()

    def test_httpretty_is_enabled(self):
        assert httpretty.is_enabled() is True


class TestNfsnConstructor(NfsnTest):

    def test_constructor_no_args_file_missing(self, monkeypatch, tmpdir):
        monkeypatch.setenv('HOME', str(tmpdir))
        with pytest.raises(IOError):
            Nfsn()

    def test_constructor_missing_api_key(self):
        with pytest.raises(ValueError):
            Nfsn(login='guest')

    def test_constructor_missing_login(self):
        with pytest.raises(ValueError):
            Nfsn(api_key='1234567890123456')

    def test_constructor_login_and_key(self):
        nfsn = Nfsn(login='guest', api_key='1234567890123456')
        assert type(nfsn) is Nfsn

    def test_constructor_loginfile(self):
        login_file = os.path.join(fixtures_dir, 'nfsn-api-credential')
        nfsn = Nfsn(login_file=login_file)
        assert type(nfsn) is Nfsn

    def test_constructor_implicit_loginfile(self, monkeypatch, tmpdir):
        login_file = os.path.join(fixtures_dir, 'nfsn-api-credential')
        copyfile(login_file, str(tmpdir.join('.nfsn-api')))
        monkeypatch.setenv('HOME', str(tmpdir))
        nfsn = Nfsn()
        assert type(nfsn) is Nfsn

class TestNfsnAccount(NfsnTest):

    def setup(self):
        self.account = self.nfsn.account('A1B2-C3D4E5F6')

    def test_get_balance(self):
        result = self.account.balance
        assert result == 9.04

    def test_get_friendly_name(self):
        result = self.account.friendlyName
        assert result == 'Personal'

    def test_set_friendly_name(self):
        result = self.account.friendlyName = 'Business'
        assert result == 'Business'

    def test_get_status(self):
        expected = {
          'color': '#00b000',
          'short': 'OK',
          'status': 'Ok',
        }
        result = self.account.status
        assert +result == expected

    def test_get_sites(self):
        expected = [ 'coolsite', 'anothercoolsite' ]
        result = self.account.sites
        assert result == expected

    def test_add_site(self):
        result = self.account.addSite(site='testing')
        assert result == ''

    def test_add_warning(self):
        result = self.account.addWarning(balance=1.23)
        assert result == ''

    def test_remove_warning(self):
        result = self.account.removeWarning(balance=1.23)
        assert result == ''


class TestNfsnDns(NfsnTest):

    def setup(self):
        self.dns = self.nfsn.dns('example.com')

    def test_get_expire(self):
        result = self.dns.expire
        assert result == 86400

    def test_set_expire(self):
        result = self.dns.expire = 86401
        assert result == 86401

    def test_get_minttl(self):
        result = self.dns.minTTL
        assert result == 180

    def test_get_refresh(self):
        result = self.dns.refresh
        assert result == 600

    def test_get_retry(self):
        result = self.dns.retry
        assert result == 180

    def test_get_serial(self):
        result = self.dns.serial
        assert result == 1414129428

    def test_addrr_without_ttl(self):
        result = self.dns.addRR(
            name = 'testing',
            type = 'A',
            data = '192.0.2.2'
        )
        assert result == ''

    def test_addrr_with_ttl(self):
        result = self.dns.addRR(
            name = 'testing',
            type = 'A',
            data = '192.0.2.2',
            ttl = '3600'
        )
        assert result == ''

    def test_listrrs(self):
        expected = [
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
        result = self.dns.listRRs()
        assert result == expected

    def test_listrrs_with_parameters(self):
        # Don't bother checking the return values (the fixture result is not
        # really accurate). Just sanity-check that these parameters don't
        # raise any errors:
        assert self.dns.listRRs(name='foo')
        assert self.dns.listRRs(type='NS')
        assert self.dns.listRRs(data='192.0.2.1')

    def test_removeRR(self):
        result = self.dns.removeRR(
            name = 'testing',
            type = 'A',
            data = '192.0.2.2'
        )
        assert result == ''

    def test_update_serial(self):
        result = self.dns.updateSerial()
        assert result == ''


class TestNfsnEmail(NfsnTest):

    def setup(self):
        self.email = self.nfsn.email('example.com')

    def test_list_forwards(self):
        result = self.email.listForwards()
        assert result == { 'hello': 'customerservice@example.net'}

    def test_removeForward(self):
        result = self.email.removeForward(forward='hi')
        assert result == ''

    def test_setForward(self):
        result = self.email.setForward(forward='hi', dest_email='h@example.net')
        assert result == ''


class TestNfsnMember(NfsnTest):

    def setup(self):
        self.member = self.nfsn.member('guest')

    def test_get_accounts(self):
        result = self.member.accounts
        assert result == [ 'A1B2-C3D4E5F6' ]

    def test_get_sites(self):
        result = self.member.sites
        assert result == [ 'coolsite', 'anothercoolsite' ]


class TestNfsnSite(NfsnTest):

    def setup(self):
        self.site = self.nfsn.site('mycoolsite')

    def test_add_alias(self):
        result = self.site.addAlias(alias='mobile.example.com')
        assert result == ''

    def test_remove_alias(self):
        result = self.site.removeAlias(alias='mobile.example.com')
        assert result == ''
