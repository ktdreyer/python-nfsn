import hashlib
import logging
import random
import requests
import string
import time
try:
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

class NfsnAuth(requests.auth.AuthBase):
    """Helper class for NearlyFreeSpeech authentication using requests
       library.
       :Example:
       >>> s = requests.Session()
       >>> s.auth = NfsnAuth('myusername', 'myapikey1234')
       >>> nfsn = NfsnBeanbag('https://api.nearlyfreespeech.net', session=s)
    """
    SALT_CHARACTERS = string.ascii_letters + string.digits

    def __init__(self, login, api_key):
        self.login = login
        self.api_key = api_key

    def __call__(self, r):
        """ API requests must include a custom X-NFSN-Authentication HTTP
        header. See
        https://members.nearlyfreespeech.net/wiki/API/Introduction for
        more explanation. """

        header = self._header(r)
        log.debug("X-NFSN-Authentication header: %s", header)

        r.headers['X-NFSN-Authentication'] = header
        return r

    def _header(self, r):
        """ Build the contents of the X-NFSN-Authentication HTTP header. See
        https://members.nearlyfreespeech.net/wiki/API/Introduction for
        more explanation. """
        login = self.login
        timestamp = self._timestamp()
        salt = self._salt()
        api_key = self.api_key
        request_uri = urlparse(r.url).path
        body = ''.encode('utf-8')
        if r.body:
            body = r.body.encode('utf-8')
        body_hash = hashlib.sha1(body).hexdigest()

        log.debug("login: %s", login)
        log.debug("timestamp: %s", timestamp)
        log.debug("salt: %s", salt)
        log.debug("api_key: %s", api_key)
        log.debug("request_uri: %s", request_uri)
        log.debug("body_hash: %s", body_hash)

        string = ';'.join((login, timestamp, salt, api_key, request_uri, body_hash))
        log.debug("string to be hashed: %s", string)
        string_hash = hashlib.sha1(string.encode('utf-8')).hexdigest()
        log.debug("string_hash: %s", string_hash)

        return ';'.join((login, timestamp, salt, string_hash))


    def _salt(self):
        """ Return a 16-character alphanumeric string. """
        return ''.join(random.SystemRandom().choice(self.SALT_CHARACTERS) for _ in range(16))

    def _timestamp(self):
        """ Return the current number of seconds since the Unix epoch,
        as a string. """
        return str(int(time.time()))

