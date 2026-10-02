#!/usr/bin/env python3
"""Check a sending domain's email authentication records over public DNS-over-HTTPS.

Usage: python3 check_domain.py example.com [dkim_selector ...]

Standard library only. Queries https://dns.google/resolve, so it needs outbound HTTPS.
Prints MX, SPF, DMARC and DKIM findings as plain text. Read-only: it changes nothing.
"""
import json
import re
import sys
import urllib.parse
import urllib.request

DOH = "https://dns.google/resolve"
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
SELECTOR_RE = re.compile(r"^[A-Za-z0-9._-]{1,63}$")
SPF_LOOKUP_LIMIT = 10
COMMON_SELECTORS = [
    "google", "selector1", "selector2", "default", "k1", "k2", "s1", "s2",
    "dkim", "mail", "smtp", "mx", "zoho", "protonmail", "protonmail2", "sig1",
    "hostingermail-a", "hostingermail-b", "mxvault", "everlytickey1", "fm1",
]


def query(name: str, rtype: str) -> list[str]:
    url = f"{DOH}?{urllib.parse.urlencode({'name': name, 'type': rtype})}"
    req = urllib.request.Request(url, headers={"accept": "application/dns-json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read(1_000_000))
    return [clean(a.get("data", "")) for a in data.get("Answer", [])]


def clean(record: str) -> str:
    # DNS text is set by the domain owner: keep printable chars only, cap length.
    record = record.strip('"').replace('" "', "")
    return "".join(c for c in record if c.isprintable())[:512]


def txt_records(name: str) -> list[str]:
    return query(name, "TXT")


def check_spf(domain: str) -> list[str]:
    spf = [r for r in txt_records(domain) if r.lower().startswith("v=spf1")]
    if not spf:
        return ["FAIL  SPF: no v=spf1 record found"]
    out = []
    if len(spf) > 1:
        out.append(f"FAIL  SPF: {len(spf)} SPF records, only one is allowed")
    rec = spf[0]
    out.append(f"OK    SPF: {rec}")
    terms = rec.lower().split()[1:]
    lookups = 0
    for term in terms:
        mech = term.lstrip("+-~?")
        if mech.startswith(("include:", "exists:", "redirect=", "ptr")) or mech in ("a", "mx") \
                or mech.startswith(("a:", "a/", "mx:", "mx/")):
            lookups += 1
    if lookups > SPF_LOOKUP_LIMIT:
        out.append(f"FAIL  SPF: about {lookups} DNS lookups at top level, limit is 10 including nested")
    all_terms = [t for t in terms if t.lstrip("+-~?") == "all"]
    has_redirect = any(t.startswith("redirect=") for t in terms)
    if not all_terms and not has_redirect:
        out.append("FAIL  SPF: no 'all' mechanism and no redirect=, so the policy is open-ended")
    for term in all_terms:
        if term in ("+all", "all"):
            out.append("FAIL  SPF: +all (or bare all) lets anyone send as you")
        elif term == "?all":
            out.append("WARN  SPF: ?all is neutral, use ~all or -all")
    return out


def check_dmarc(domain: str) -> list[str]:
    recs = [r for r in txt_records(f"_dmarc.{domain}") if r.lower().startswith("v=dmarc1")]
    if not recs:
        return ["FAIL  DMARC: no record at _dmarc." + domain]
    rec = recs[0]
    tags = dict(p.strip().split("=", 1) for p in rec.split(";") if "=" in p)
    tags = {k.strip().lower(): v.strip() for k, v in tags.items()}
    policy = tags.get("p", "").lower()
    out = [f"OK    DMARC: {rec}"]
    if policy == "none":
        out.append("WARN  DMARC: p=none only monitors. Move to quarantine once reports look clean")
    if "rua" not in tags:
        out.append("WARN  DMARC: no rua= address, so you receive no aggregate reports")
    return out


def check_dkim(domain: str, selectors: list[str]) -> list[str]:
    found = []
    for sel in selectors:
        try:
            recs = query(f"{sel}._domainkey.{domain}", "TXT")
        except Exception:
            continue
        hits = [r for r in recs if "p=" in r]
        if hits:
            found.append(f"OK    DKIM: selector '{sel}' published")
    if not found:
        return ["WARN  DKIM: none of the common selectors found. Ask your email provider for the "
                "selector name and rerun with it as an argument"]
    return found


def check_mx(domain: str) -> list[str]:
    mx = query(domain, "MX")
    if not mx:
        return ["WARN  MX: no MX records, replies to this domain will bounce"]
    return [f"OK    MX: {', '.join(sorted(mx))}"]


def normalise_domain(raw: str) -> str:
    host = raw.lower().strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    host = host.split("@")[-1].rstrip(".")
    if not DOMAIN_RE.match(host):
        raise ValueError(f"not a valid domain: {raw!r}")
    return host


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    try:
        domain = normalise_domain(argv[1])
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 2
    selectors = [s for s in argv[2:] if SELECTOR_RE.match(s)] or COMMON_SELECTORS
    print(f"Domain: {domain}")
    for check in (check_mx, check_spf, check_dmarc):
        try:
            print("\n".join(check(domain)))
        except Exception as exc:  # network or parse failure
            print(f"ERROR {check.__name__}: {exc}")
    try:
        print("\n".join(check_dkim(domain, selectors)))
    except Exception as exc:
        print(f"ERROR check_dkim: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
