#!/usr/bin/env python3
from datetime import datetime, timezone
import os
import re
import subprocess


def convertHostname(name, domain):
    if ':' in name:
        host, port = name.split(':')
        return '[%s.%s]:%s' % (host, domain, port)
    return '%s.%s' % (name, domain)


def writePubKeysForHost(outfile, dirname):
    hostnamespath = os.path.join(dir, 'hostnames')

    with open(hostnamespath) as f:
        hostnames = ','.join(convertHostname(name.strip(), domain) for name in f if not re.match(r'\s*($|#)', name))

    for keyfile in (os.path.join(dir, keyname) for keyname in  os.listdir(dir) if keyname.endswith('_key.pub')):
        with open(keyfile) as f:
            print(hostnames, f.read().strip(), file=outfile)


def appendToFile(src_path, dst_file):
    with open(src_path) as src_file:
        for buffer in iter(lambda : src_file.read(4096), ''):
            dst_file.write(buffer)


def createHashedCopy(src, dst, ts=False):
    with open(dst, "w") as f:
        if ts: print(timestamp, file=f)
        appendToFile(src, f)

    subprocess.check_call(['ssh-keygen', '-H', '-f', dst ])
    os.unlink("%s.old" % dst)


path_unhashed = 'known_hosts_unhashed'
path_hashed = 'known_hosts_hashed'
path_unhashed_full = 'known_hosts_unhashed_full'
path_hashed_full = 'known_hosts_hashed_full'
domainpath = 'domain'
timestamp = "### generated on %s ###\n" % datetime.utcnow().replace(tzinfo=timezone.utc).astimezone().isoformat()

if not os.path.exists(domainpath):
        raise Exception("Mandatory file '%s' is missing." % domain)

with open(domainpath) as f:
        domain = f.read().strip()


## create hashed known_hosts
print(path_unhashed, path_hashed)
createHashedCopy(path_unhashed, path_hashed, ts=True)


## create unhashed known_hosts for all hosts
with open(path_unhashed_full, "w") as f:
    print(timestamp, file=f)
    appendToFile(path_unhashed, f)

    print("\n# Hosts with certificates", file=f)
    for dir in (path for path in os.listdir() if os.path.isdir(path)):
        writePubKeysForHost(f, dir)


## create hashed known_hosts for all hosts
createHashedCopy(path_unhashed_full, path_hashed_full)
