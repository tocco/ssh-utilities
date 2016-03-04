#!/usr/bin/env python3
from datetime import datetime, timezone
import re
import os


def getDateFromFile(dir, file):
    expfile = os.path.join(dir, file)
    if not os.path.exists(expfile):
        return

    with open(expfile) as f:
        return datetime.strptime(f.read().strip(), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone()

def getHostNameCount(dir):
    path = os.path.join(dir, 'hostnames')
    if not os.path.exists(path):
        return 0

    with open(path) as f:
        return sum(not re.match(r'\s*($|#)', fname) for fname in f)

def getCertCount(dir):
    return sum(i.endswith('_key.pub') for i in os.listdir(dir))

exp_dates = []
for dir in (path for path in os.listdir() if os.path.isdir(path)):
    exp_dates.append([dir, getDateFromFile(dir, 'issue_date'), getDateFromFile(dir, 'expiration_date'), getHostNameCount(dir), getCertCount(dir)])

exp_dates.sort(key=lambda i: (i[2], i[0]) if i[2] != None else (datetime.min.replace(tzinfo=timezone.utc), i[0]))

now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone()
print("%-16s %-11s %-11s %-9s %5s %5s" % ("HOST / DIR", "ISSUED ON", "EXPIRES ON", "EXP. IN", "FQDNs", "KEYS"))
for host, issued_date, exp_date, host_count, cert_count in exp_dates:
    issued = issued_date.date() if issued_date != None else 'unknown'
    exp = exp_date.date() if exp_date != None else 'unknown'
    diff = "%s days" % (exp_date-now).days if exp_date != None else 'unknown'

    print("%-16s %-11s %-11s %9s %5d %5d" % (host, issued, exp, diff, host_count, cert_count))

print()
print(" SUMMARY ".center(40, '-'))
fmt="%6d %-25s"
print(fmt % (len(exp_dates), "hosts / directories"))
print(fmt % (sum(i[3] for i in exp_dates), "FQDNs / hostnames"))
print(fmt % (sum(i[4] for i in exp_dates), "keys (public keys)"))
print(fmt % (sum(i[3]*i[4] for i in exp_dates), "hashed known_hosts entries"))
print('-'*40)
