import nfsn.cli
import sys

class TestNfsnCliHelp(object):

    expected_help = 'pynfsn: Interact with the NearlyFreeSpeech.net API.'

    def test_print_help(self, capsys):
        nfsn.cli.print_help('pynfsn')
        (out, _) = capsys.readouterr()
        assert out.find(self.expected_help) > -1

    def test_main_sys_argv(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, 'argv', ['pynfsn'])
        nfsn.cli.main()
        (out, _) = capsys.readouterr()
        assert out.find(self.expected_help) > -1

    def test_main_no_args(self, capsys):
        nfsn.cli.main(['pynfsn'])
        (out, _) = capsys.readouterr()
        assert out.find(self.expected_help) > -1

    def test_main_one_arg(self, capsys):
        nfsn.cli.main(['pynfsn', 'dns'])
        (out, _) = capsys.readouterr()
        assert out.find(self.expected_help) > -1


class DummyNfsn(object):
    def dns(self, domain):
        return DummyNfsnDns()

class DummyNfsnDns(object):
    expires = 864000
    def listRRs(self):
        return [{'data': 'www.example.com'}]

class TestNfsnCli(object):

    def test_dns_expires(self, monkeypatch, capsys):
        monkeypatch.setattr(nfsn, 'Nfsn', DummyNfsn)
        nfsn.cli.main(['pynfsn', 'dns', 'example.com', 'expires'])
        (out, _) = capsys.readouterr()
        assert out == "864000\n"

    def test_dns_listrrs(self, monkeypatch, capsys):
        monkeypatch.setattr(nfsn, 'Nfsn', DummyNfsn)
        nfsn.cli.main(['pynfsn', 'dns', 'example.com', 'listRRs'])
        (out, _) = capsys.readouterr()
        return out == str([{'data': 'www.example.com'}])
