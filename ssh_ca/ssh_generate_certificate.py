#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
import os
import re
import shlex
import subprocess
import sys


class CertError(Exception):
    pass


def convertHostname(name, domain):
        if ':' in name:
                # Port numbers are not currently supported in certificates.
                return '%s.%s' % (name.split(':')[0], domain)
        return '%s.%s' % (name, domain)


def checkWeakKeys(keys):
    for key in keys:
        output = subprocess.check_output(['ssh-keygen', '-l', '-f', key ]).decode()
        keysize, algo = re.match(r'(\d+) .*\(([^(]+)\)$', output).groups()
        keysize = int(keysize)

        if algo == "DSA" or algo == "RSA" and keysize < 2048:
            raise CertError("Declining to certify weak key with algorithm %s and size of %d bits located at '%s'" % (algo, keysize, key))


if len(sys.argv) != 2:
        print("Usage: %s HOSTNAME" % sys.argv[0])
        exit(1)


basename = os.path.normpath(sys.argv[1])
hostnamespath = os.path.join(basename, 'hostnames')
serialpath = 'serial'
expirationpath = os.path.join(basename, 'expiration_date')
issuepath = os.path.join(basename, 'issue_date')
logfile = os.path.join(basename, 'log')
globallog = 'log'
validityfile = os.path.join(basename, 'validity')
domainpath = 'domain'

if not os.path.exists(domainpath):
	raise CertError("Mandatory file '%s' is missing." % domainpath)

with open(domainpath) as f:
	domain = f.read().strip()

with open(hostnamespath) as f:
    hostnames = ','.join(convertHostname(name.strip(), domain) for name in f if not re.match(r'\s*($|#)', name))
if not hostnames:
    raise CertError("No hostnames found in '%s'" % hostnamespath)

public_keys = [ os.path.join(basename, keyname) for keyname in  os.listdir(basename) if keyname.endswith('_key.pub') ]
if not public_keys:
    raise CertError("No public keys found.")

checkWeakKeys(public_keys)

if os.path.exists(serialpath):
    with open(serialpath) as f:
        serial = 1 + int(f.read().strip())
else:
    serial = 1

if os.path.exists(validityfile):
    with open(validityfile) as f:
        validity = int(f.read().strip())
else:
    validity = 730


valid_until = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone() + timedelta(days=validity)


command = [ 'ssh-keygen', '-s', 'authority', '-I', basename, '-h', '-n', hostnames, '-V', valid_until.strftime("-15m:%Y%m%d%H%M%S"), '-z', str(serial) ] + public_keys
command_quoted = ' '.join(shlex.quote(arg) for arg in command)
print(command_quoted)
input(' ** hit enter to execute **')
ts = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone()
with open(logfile, "a") as log:
    print("\n** %s **\n" % ts, file=log)
    print("executing:", command_quoted, file=log)
    log.flush()
    rc = subprocess.call(command, stdout=log, stderr=log)
    if rc:
        raise CertError("error: Command returned non-zero status %s. See log file '%s' for details." % (rc, logfile))

with open(serialpath, "w") as f:
    print(serial, file=f)

with open(issuepath, "w") as f:
    print(ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), file=f)

with open(expirationpath, "w") as f:
    print(valid_until.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), file=f)

with open(globallog, "a") as f:
    print("%s - serial: %3d, host: %s, validity: %d days, hostnames: %s" % (ts, serial, basename, validity, hostnames), file=f)
