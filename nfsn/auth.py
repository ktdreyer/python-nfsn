import hashlib
import logging
import random
import requests
import string
import time
import urlparse

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
        request_uri = urlparse.urlparse(r.url).path
        body_hash = hashlib.sha1(r.body or '').hexdigest()

        log.debug("login: %s", login)
        log.debug("timestamp: %s", timestamp)
        log.debug("salt: %s", salt)
        log.debug("api_key: %s", api_key)
        log.debug("request_uri: %s", request_uri)
        log.debug("body_hash: %s", body_hash)

        string = ';'.join((login, timestamp, salt, api_key, request_uri, body_hash))
        log.debug("string to be hashed: %s", string)
        string_hash = hashlib.sha1(string).hexdigest()
        log.debug("string_hash: %s", string_hash)

        return ';'.join((login, timestamp, salt, string_hash))


    def _salt(self):
        return ''.join(random.SystemRandom().choice(self.SALT_CHARACTERS) for _ in range(16))

    def _timestamp(self):
        return str(int(time.time()))

