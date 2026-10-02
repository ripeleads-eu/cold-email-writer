"""Offline tests for the deliverability DNS checker. DNS is stubbed; no network."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/email-deliverability-check/scripts/check_domain.py"
spec = importlib.util.spec_from_file_location("check_domain", SCRIPT)
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)


def stub(records):
    return lambda name, rtype: records.get((name, rtype), [])


def test_spf_ok_and_softfail(monkeypatch):
    monkeypatch.setattr(cd, "query", stub({("x.com", "TXT"): ["v=spf1 include:_spf.google.com ~all"]}))
    out = cd.check_spf("x.com")
    assert out[0].startswith("OK")
    assert len(out) == 1


def test_spf_missing_and_duplicate_and_plus_all(monkeypatch):
    monkeypatch.setattr(cd, "query", stub({}))
    assert cd.check_spf("x.com")[0].startswith("FAIL")
    monkeypatch.setattr(cd, "query", stub({("x.com", "TXT"): ["v=spf1 +all", "v=spf1 -all"]}))
    out = " ".join(cd.check_spf("x.com"))
    assert "only one is allowed" in out and "+all" in out


def test_dmarc_none_without_rua(monkeypatch):
    monkeypatch.setattr(cd, "query", stub({("_dmarc.x.com", "TXT"): ["v=DMARC1; p=none"]}))
    out = " ".join(cd.check_dmarc("x.com"))
    assert "p=none only monitors" in out and "no rua=" in out


def test_dmarc_missing(monkeypatch):
    monkeypatch.setattr(cd, "query", stub({}))
    assert cd.check_dmarc("x.com")[0].startswith("FAIL")


def test_dkim_found_and_missing(monkeypatch):
    monkeypatch.setattr(cd, "query", stub({("s1._domainkey.x.com", "TXT"): ["v=DKIM1; k=rsa; p=MIIB"]}))
    assert cd.check_dkim("x.com", ["s1", "s2"]) == ["OK    DKIM: selector 's1' published"]
    assert cd.check_dkim("x.com", ["zz"])[0].startswith("WARN")


def test_mx(monkeypatch):
    monkeypatch.setattr(cd, "query", stub({("x.com", "MX"): ["10 mx.x.com."]}))
    assert cd.check_mx("x.com")[0].startswith("OK")
    monkeypatch.setattr(cd, "query", stub({}))
    assert cd.check_mx("x.com")[0].startswith("WARN")


@pytest.mark.parametrize("raw,expected", [
    ("Example.com", "example.com"),
    ("https://example.com/path", "example.com"),
    ("anna@example.co.uk", "example.co.uk"),
])
def test_normalise_domain(raw, expected):
    assert cd.normalise_domain(raw) == expected


@pytest.mark.parametrize("raw", ["", "not a domain", "x;rm -rf", "localhost"])
def test_normalise_domain_rejects(raw):
    with pytest.raises(ValueError):
        cd.normalise_domain(raw)


def test_main_usage_and_bad_domain(capsys):
    assert cd.main(["check_domain.py"]) == 2
    assert cd.main(["check_domain.py", "bad domain"]) == 2


def test_query_parses_doh_json(monkeypatch):
    payload = json.dumps({"Answer": [{"data": '"v=spf1 " "-all"'}]}).encode()

    class Resp:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def read(self, *a):
            return payload

    monkeypatch.setattr(cd.urllib.request, "urlopen", lambda req, timeout: Resp())
    assert cd.query("x.com", "TXT") == ["v=spf1 -all"]


def _spf(monkeypatch, rec):
    monkeypatch.setattr(cd, "query", stub({("x.com", "TXT"): [rec]}))
    return " ".join(cd.check_spf("x.com"))


def test_spf_bare_all_fails(monkeypatch):
    out = _spf(monkeypatch, "v=spf1 include:_spf.google.com all")
    assert "FAIL" in out and "anyone send" in out


def test_spf_no_all_and_no_redirect_fails(monkeypatch):
    assert "no 'all' mechanism" in _spf(monkeypatch, "v=spf1 include:_spf.google.com")
    assert "no 'all' mechanism" not in _spf(monkeypatch, "v=spf1 redirect=_spf.example.com")


def test_spf_lookup_limit(monkeypatch):
    ten = "v=spf1 " + " ".join(f"include:s{i}.example.com" for i in range(10)) + " -all"
    eleven = "v=spf1 " + " ".join(f"include:s{i}.example.com" for i in range(11)) + " -all"
    assert "DNS lookups" not in _spf(monkeypatch, ten)
    assert "FAIL  SPF: about 11 DNS lookups" in _spf(monkeypatch, eleven)
