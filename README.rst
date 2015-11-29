`python-nfsn`
=============

.. image:: https://travis-ci.org/ktdreyer/python-nfsn.svg?branch=master
       :target: https://travis-ci.org/ktdreyer/python-nfsn

.. image:: https://coveralls.io/repos/ktdreyer/python-nfsn/badge.svg?branch=master&service=github
     :target: https://coveralls.io/github/ktdreyer/python-nfsn?branch=master

.. image:: https://badge.fury.io/py/python-nfsn.svg
          :target: https://badge.fury.io/py/python-nfsn

A modern Python library for accessing NearlyFreeSpeech.net's API.

* Clean, Pythonic API
* Supports 100% of NFSN's API (as of "today" :)
* Supports Python 2.6 through 3.5
* Good test coverage (using ``httpretty``)
* Cryptographically secure salt generation with ``random.SystemRandom()``

Installing
----------

To get running quickly, install from PyPI::

    pip install python-nfsn

This will place a ``pynfsn`` uility in your ``$PATH``.

If you want to hack on the code::

    git clone https://github.com/ktdreyer/python-nfsn
    cd python-nfsn
    virtualenv venv
    . venv/bin/activate
    python setup.py develop


Quickstart
==========

Obtain your API key from NFSN by submitting a secure support request via the
control panel, and store it in a JSON file in your home directory, like so::

    $ cat ~/.nfsn-api
    { "login": "ktdreyer",  "api-key": "aGVsbG90aGVyZWZyaWVuZA" }

Use the ``pynfsn`` command-line utility, a thin wrapper that lets you explore
the API ::

    $ pynfsn member ktdreyer accounts
    [u'D41D-8CD98F00', u'B204-E9800998', u'ECF8-427E6D7F']

    $ pynfsn member ktdreyer sites
    [u'coolsite', u'anothercoolsite']

    $ pynfsn dns example.com listRRs www
    [{u'data': u'example.nfshost.com.', u'scope': u'system', u'type': u'CNAME', u'name': u'www', u'ttl': u'600'}]

    $ pynfsn dns example.com addRR testing A 192.0.2.2

    $ pynfsn dns example.com removeRR testing A 192.0.2.2


Or use the API directly in your own code:

.. code-block:: python

    from nfsn import Nfsn

    nfsn = Nfsn(login='myusername', api_key='aGVsbG90aGVyZWZyaWVuZA')

    rrs = nfsn.dns('example.com').listRRs(name='www')
    for rr in rrs:
        print(rr['name']) # eg. 'www'
        print(rr['type']) # eg. 'A'
        print(rr['data']) # eg. '192.0.2.2'


Authentication
==============

There are three ways to pass your authentication credentials to the ``Nfsn()``
constructor:

1) Call the constructor with no arguments:

   .. code-block:: python

       n = Nfsn()

   By default, the library will look for a ``$HOME/.nfsn-api`` JSON file that
   contains your username and API key, like so::

    $ cat ~/.nfsn-api
    { "login": "ktdreyer",  "api-key": "aGVsbG90aGVyZWZyaWVuZA" }

   (This matches the same file and format that the Perl NFSN API uses for
   authentication, by the way.)

2) Call the constructor with an explicit path to an API key login file:

   .. code-block:: python

       n = Nfsn(login_file='/etc/nfsn-api')

   In this example, the ``login_file`` should be a JSON file, similar to the
   example above.

3) Specify a login string and API key string directly. You can skip the JSON
   login_file altogether and just pass the strings you need:

   .. code-block:: python

       n = Nfsn(login='ktdreyer', api_key='aGVsbG90aGVyZWZyaWVuZA')

If you do not enter the correct login and key combination, each time you access
a property or method using this library (see below), NearlyFreeSpeech.net will
return a HTTP 401 error, and this library will raise a ``RuntimeError``.


API Examples
============

See https://members.nearlyfreespeech.net/wiki/API for more information.


Account API
-----------

.. code-block:: python

    from nfsn import Nfsn

    nfsn = Nfsn(login='ktdreyer', api_key='aGVsbG90aGVyZWZyaWVuZA')

    # A floating-point value, the balance on the account.
    # Example: 9.04
    nfsn.account('A1B2-C3D4E5F6').balance

    # The friendly, human-readable name for an account.
    # Example: "Personal" or "Business"
    nfsn.account('A1B2-C3D4E5F6').friendlyName
    nfsn.account('A1B2-C3D4E5F6').friendlyName = 'Business'

    # The status details for an account.
    # Example: { 'color': '#00b000', 'short': 'OK', 'status': 'Ok' }
    # (Note: returns an AttrDict)
    nfsn.account('A1B2-C3D4E5F6').status

    # The sites associated with an account.
    # Example: [ 'coolsite', 'anothercoolsite' ]
    nfsn.account('A1B2-C3D4E5F6').sites

    # Add a new site to an account.
    nfsn.account('A1B2-C3D4E5F6').addSite(site='testing')

    # Add a new warning to an account.
    nfsn.account('A1B2-C3D4E5F6').addWarning(balance=1.23)

    # Remove a warning from an account.
    nfsn.account('A1B2-C3D4E5F6').removeWarning(balance=1.23)

DNS API
-------

.. code-block:: python

    from nfsn import Nfsn

    nfsn = Nfsn(login='ktdreyer', api_key='aGVsbG90aGVyZWZyaWVuZA')

    # Get or set the expiration value for a DNS zone.
    nfsn.dns('example.com').expire # Example: 86400
    nfsn.dns('example.com').expire = 86401

    # Get the minTTL value for a DNS zone.
    # Example: 180
    nfsn.dns('example.com').minTTL

    # Get the minTTL value for a DNS zone.
    # Example: 600
    nfsn.dns('example.com').refresh

    # Get the retry value for a DNS zone.
    # Example: 180
    nfsn.dns('example.com').retry

    # Get the serial value for a DNS zone.
    # Example: 1414129428
    nfsn.dns('example.com').serial

    # Add a DNS resource record. The name+type must not exist yet.
    nfsn.dns('example.com').addRR(
        name = 'testing',
        type = 'A',
        data = '192.0.2.2'
    )

    # List all DNS resource records:
    # (Note: returns an AttrDict)
    # Example:
    #    [{'data':  '192.0.2.1',
    #      'name':  '',
    #      'scope': 'member',
    #      'ttl':   '3600',
    #      'type':  'A'},
    #     {'data':  'ns.phx2.nearlyfreespeech.net.',
    #      'name':  '',
    #      'scope': 'member',
    #      'ttl':   '3600',
    #      'type':  'NS'}]
    nfsn.dns('example.com').listRRs()

    # List all DNS resource records for 'www.example.com':
    # (Note: returns an AttrDict)
    # Example:
    #    [{'data':  '192.0.2.1',
    #      'name':  'www',
    #      'scope': 'member',
    #      'ttl':   '3600',
    #      'type':  'A'}]
    nfsn.dns('example.com').listRRs(name='www')

    # Add a DNS resource record.
    # The name+type must exist, or Nfsn will raise an an error. You must
    # specify all three parameters (name, type, data).
    nfsn.dns('example.com').removeRR(
        name = 'testing',
        type = 'A',
        data = '192.0.2.2'
    )


Email API
---------

.. code-block:: python

    from nfsn import Nfsn

    nfsn = Nfsn(login='ktdreyer', api_key='aGVsbG90aGVyZWZyaWVuZA')

    # List all email forwarding.
    # Example: { 'hello': 'customerservice@example.net'}
    # (Note: returns an AttrDict)
    nfsn.email('example.com').listForwards()

    # Forward all 'hi@example.com' mail to 'h@example.net':
    nfsn.email('example.com').setForward(forward='hi', dest_email='h@example.net')
    # ... And remove the email forward:
    nfsn.email('example.com').removeForward(forward='hi')


Member API
----------

.. code-block:: python

    from nfsn import Nfsn

    nfsn = Nfsn(login='ktdreyer', api_key='aGVsbG90aGVyZWZyaWVuZA')

    # Get a list of all accounts belonging to a member.
    # Example: [ 'A1B2-C3D4E5F6' ]
    nfsn.member('ktdreyer').accounts

    # Get a list of all sites belonging to a member.
    # Example: [ 'coolsite', 'anothercoolsite' ]
    nfsn.member('ktdreyer').sites

Site API
--------

.. code-block:: python

    from nfsn import Nfsn

    nfsn = Nfsn(login='ktdreyer', api_key='aGVsbG90aGVyZWZyaWVuZA')

    # Add or remove an alias for a site:
    nfsn.site('mycoolsite').addAlias(alias='mobile.example.com')
    nfsn.site('mycoolsite').removeAlias(alias='mobile.example.com')


Types and Errors
================

Note that since we use `Beanbag <https://pypi.python.org/pypi/beanbag>`_
internally, when we return a dict value, it is really an `AttrDict
<https://pypi.python.org/pypi/attrdict>`_. If you want to convert the value to
a plain dict, you will need to use the ``+`` operator. Prepend the value with a
``+`` sign, like so:

.. code-block:: python

    rrs = nfsn.dns('example.com').listRRs()
    print +rrs

If you try to access a non-existent property or method, NearlyFreeSpeech.net
will return a HTTP 404 Not Found error, and this library will raise a
``BeanBagException``.


License and Copyright
=====================

This software is CC0 1.0 Universal (CC0 1.0) Public Domain Dedication. See
``COPYING`` for the full CC0 text.
