from beanbag.v2 import BeanBag, Request, BeanBagException
import json
import logging

log = logging.getLogger(__name__)

class NfsnBeanBag(BeanBag):
    """Tweak functionality in the BeanBag class to work with NFSN."""

    def encode(self, body):
        """ Beanbag encodes the body as JSON, but NFSN expects the body to be
        regular key-value pairs that are not JSON-encoded. """
        if isinstance(body, Request):
            req = body
        elif isinstance(body, int):
            body = str(body)
        req = Request(data=body, headers={'Accept': self.mime_json})
        return super(~NfsnBeanBag, self).encode(req)

    def decode(self, response):
        """ Handle 'Unauthorized' response """
        if response.status_code == 401:
            log.error(response.content)
            raise RuntimeError('Could not authenticate with login/key.')

        # NFSN sometimes returns simple strings rather than JSON.
        try:
            json.loads(response.content.decode('utf-8'))
        except ValueError as e:
            #log.debug("%s : %s" % (e, response.content))
            # Assume NFSN responded with a simple string (not JSON).
            return response.content.decode('utf-8')

        # NFSN sends JSON in the HTTP body, but the Content-Type HTTP header
        # "application/x-nfsn-api". Set this content-type to JSON so BeanBag
        # will parse it.
        res_content = response.headers.get('content-type', None)
        if res_content is None:
            # Not sure this can ever happen?
            log.debug('found no Content-Type header')
        elif res_content == 'application/x-nfsn-api':
            log.debug("found 'application/x-nfsn-api' Content-Type")
            log.debug("Changing Content-Type to 'application/json'")
            response.headers['content-type'] = self.mime_json

        # Provide logging for other errors
        try:
            return super(~NfsnBeanBag, self).decode(response)
        except BeanBagException as e:
            log.error(e.response.headers)
            log.error(e.response.content)
            raise e
