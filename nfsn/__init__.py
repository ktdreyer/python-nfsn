from .auth import NfsnAuth
from .nfsnbeanbag import NfsnBeanBag
from beanbag.v2 import POST, GET, PUT
import json
import logging
import os
import requests

__version__ = '1.1.1'

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('nfsn')

API_ENDPOINT = 'https://api.nearlyfreespeech.net'

class Nfsn(object):
    """ Main NearlyFreeSpeech.net API object """

    def __init__(self, login=None, api_key=None, login_file=None):
        if (login is not None or api_key is not None):
            if (login is None):
                raise ValueError('specify a "login" arg when using "api_key".')
            if (api_key is None):
                raise ValueError('specify an "api_key" arg when using "login".')
            self.login = login
            self.api_key = api_key
        else:
            if (login_file is None):
                login_file = os.path.join(os.environ['HOME'], '.nfsn-api')
            with open(login_file) as data_file:
                data = json.load(data_file)
            self.login = data['login']
            self.api_key = data['api-key']

        s = requests.Session()
        s.auth = NfsnAuth(self.login, self.api_key)
        self.beanbag = NfsnBeanBag(API_ENDPOINT, session=s)

    def account(self, number):
        return NfsnAccount(nfsn=self, number=number)

    def dns(self, domain):
        return NfsnDns(nfsn=self, domain=domain)

    def email(self, domain):
        return NfsnEmail(nfsn=self, domain=domain)

    def member(self, login):
        return NfsnMember(nfsn=self, login=login)

    def site(self, name):
        return NfsnSite(nfsn=self, name=name)


class NfsnObject(object):
    def __getattr__(self, attr):
        return GET(self.beanbag[attr])

    def __setattr__(self, attr, value):
        return PUT(self.beanbag[attr], value)


class NfsnAccount(NfsnObject):
    def __init__(self, nfsn, number):
        object.__setattr__(self, 'beanbag', nfsn.beanbag.account[number])

    def addSite(self, site):
        return POST(self.beanbag.addSite, {'site': site})

    def addWarning(self, balance):
        return POST(self.beanbag.addWarning, {'balance': balance})

    def removeWarning(self, balance):
        return POST(self.beanbag.removeWarning, {'balance': balance})


class NfsnDns(NfsnObject):

    def __init__(self, nfsn, domain):
        object.__setattr__(self, 'beanbag', nfsn.beanbag.dns[domain])

    def addRR(self, name, type, data, ttl=None):
        payload = {'name': name, 'type': type, 'data': data}
        if ttl is not None:
            payload['ttl'] = ttl
        return POST(self.beanbag.addRR, payload)

    def listRRs(self, name=None, type=None, data=None):
        payload = {}
        if name is not None:
            payload['name'] = name
        if type is not None:
            payload['type'] = type
        if data is not None:
            payload['data'] = data
        return POST(self.beanbag.listRRs, payload)

    def removeRR(self, name, type, data):
        payload = {'name': name, 'type': type, 'data': data}
        return POST(self.beanbag.removeRR, payload)

    def updateSerial(self):
        return POST(self.beanbag.updateSerial)


class NfsnEmail(NfsnObject):

    def __init__(self, nfsn, domain):
        object.__setattr__(self, 'beanbag', nfsn.beanbag.email[domain])

    def listForwards(self):
        return POST(self.beanbag.listForwards)

    def removeForward(self, forward):
        return POST(self.beanbag.removeForward, {'forward': forward})

    def setForward(self, forward, dest_email):
        payload = {'forward': forward, 'dest_email': dest_email}
        return POST(self.beanbag.setForward, payload)


class NfsnMember(NfsnObject):

    def __init__(self, nfsn, login):
        object.__setattr__(self, 'beanbag', nfsn.beanbag.member[login])


class NfsnSite(NfsnObject):

    def __init__(self, nfsn, name):
        object.__setattr__(self, 'beanbag', nfsn.beanbag.site[name])

    def addAlias(self, alias):
        return POST(self.beanbag.addAlias, {'alias': alias})

    def removeAlias(self, alias):
        return POST(self.beanbag.removeAlias, {'alias': alias})
