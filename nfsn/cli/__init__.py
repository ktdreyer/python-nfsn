import os
import sys
import nfsn

_help = """%(prog)s: Interact with the NearlyFreeSpeech.net API.
Version: %(version)s
Sub Commands:
    account   Get information about a NFSN account
    dns       Get information about a NFSN DNS name
    email     Get information about a NFSN email domain
    member    Get information about a NFSN member login
    site      Get information about a NFSN site
Examples:
  List all the accounts for "myusername":
    %(prog)s member myusername accounts

  List all the sites for "myusername":
    %(prog)s member myusername sites

  Show the "friendly name" for an account:
    %(prog)s account A1B2-C3D4E5F6 friendlyName

  Show the monetary balance for an account:
    %(prog)s account A1B2-C3D4E5F6 balance

  Show all the DNS resource records for a domain:
    %(prog)s dns example.com listRRs

  Show all the DNS resource records for "www.example.com":
    %(prog)s dns example.com listRRs www

  Add a new DNS A record:
    %(prog)s dns example.com addRR testing A 192.0.2.2

  Remove a DNS record:
    %(prog)s dns example.com removeRR testing A 192.0.2.2
"""

def print_help(prog_name):
    print(_help % {'prog': prog_name, 'version': nfsn.__version__})

def main(argv=None):

    if argv is None:
        argv = sys.argv

    prog_name = os.path.basename(argv[0])

    if len(argv) <= 3:
        return print_help(prog_name)

    n = nfsn.Nfsn()

    # The HTTP call will look something like this:
    # https://api.nearlyfreespeech.net/object_name/object_id/object_action
    # where "object_name" is "dns", "email", etc.
    #       "object_id" is "example.com", "myusername", etc.
    #       "object_action" is "listRRs", "status", etc.

    (object_name, object_id, object_action) = argv[1:4]
    action_args = argv[4:]

    obj = getattr(n, object_name)(object_id)

    myproperty = getattr(obj, object_action)

    if callable(myproperty):
        result = myproperty(*action_args)
    else:
        result = myproperty

    if isinstance(result, dict):
        # AttrDict from Beanbag
        print(+result)
    else:
        print(result)
