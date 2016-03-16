# SSH Certificate Authority Utilities

## Generating a Certificate For a Host

In this example a certificate for the host **app01** with the host names
**app01.tocco.ch**, **gdt.tocco.ch** and **gdttest.tocco.ch** is created.

1. Every host has its own directory.

    ```$ mkdir app01```

2. Define host names certificate is valid for.

    ```bash
    $ cat >app01/hostnames <<EOF
    app01

    # Customers:
    gdt
    gdttest
    EOF
    ```

3. Domain automatically appended to hostnames
   ```bash
   $ echo 'mydomain.tld' >domain
   ```

4. Define how many days certificate is valid for.
  (defaults to 730 days if file is not present)
  
    ```$ echo 180 >app01/validity```

5. Copy public keys from server.

    ```$ rsync --exclude 'ssh_host_dsa_key.pub' 'app01.tocco.ch:/etc/ssh/*_key.pub' app01/```

    If key validation fails, use: -e 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

6. Generate certificate (CA's private key must be located at ./authority)

    ```bash
    $ ./ssh_generate_certificate app01
    ssh-keygen -s authority -I app01 -h -n app01.tocco.ch,gdt.tocco.ch,gdttest.tocco.ch -V -15m:20160813093145 -z 31 app01/ssh_host_rsa_key.pub app01/ssh_host_ecdsa_key.pub
    ** hit enter to execute **
    ```

7. Copy files back to server

    ```bash
    $ dest="$(ssh app01.tocco.ch mktemp -d)"
    $ scp app01/*-cert.pub "app01.tocco.ch:$dest"
    $ echo $dest
    /tmp/tmp.CHd7Ijgqr8
    $ ssh app01.tocco.ch
    $ su
    Password:
    $ cp /tmp/tmp.CHd7Ijgqr8/* /etc/ssh/
    $ rm -r /tmp/tmp.CHd7Ijgqr8
    ```

## Show Logfiles

### Show global log file

```bash
    $ tail -n 3 log
    2016-02-11 17:13:24.786902+01:00 - serial:  27, host: wiki01, validity: 730 days, hostnames: wiki01.tocco.ch
    2016-02-11 17:45:02.614714+01:00 - serial:  28, host: sfbv, validity: 730 days, hostnames: sfbv.tocco.ch
    2016-02-15 09:31:46.963660+01:00 - serial:  31, host: app01, validity: 180 days, hostnames: app01.tocco.ch,gdt.tocco.ch,gdttest.tocco.ch
```

### Show detailed log file (contains full output from ssh-keygen)

```bash
    $ cat app01/log

    ** 2016-02-15 09:31:46.963660+01:00 **

    executing: ssh-keygen -s authority -I app01 -h -n app01.tocco.ch,gdt.tocco.ch,gdttest.tocco.ch -V -15m:20160813093145 -z 31 app01/ssh_host_rsa_key.pub app01/ssh_host_ecdsa_key.pub
    Signed host key app01/ssh_host_rsa_key-cert.pub: id "app01" serial 31 for app01.tocco.ch,gdt.tocco.ch,gdttest.tocco.ch valid from 2016-02-15T09:16:46 to 2016-08-13T10:31:45
    Signed host key app01/ssh_host_ecdsa_key-cert.pub: id "app01" serial 31 for app01.tocco.ch,gdt.tocco.ch,gdttest.tocco.ch valid from 2016-02-15T09:16:46 to 2016-08-13T10:31:45
```


## List Certificates and Expiration Dates

```bash
    $ ./ssh_show_cert_list
    HOST / DIR       ISSUED ON   EXPIRES ON  EXP. IN   FQDNs  KEYS
    app06            2016-02-09  2016-08-11   177 days    75     3
    app05            2016-02-11  2016-08-11   178 days    51     2
    app03            2016-02-12  2016-08-12   179 days     1     2
       ........................................................
    tcserver01       2016-02-11  2018-02-08   724 days     5     3
    wiki01           2016-02-11  2018-02-08   724 days     1     3
    sfbv             2016-02-11  2018-02-08   724 days     1     1

    --------------- SUMMARY ----------------
      29 hosts / directories
     169 FQDNs / host names
      73 keys (host keys)
     437 hashed known_hosts entries
    ----------------------------------------
```

## Creating known_hosts Files

Create known_hosts_unhashed that contains the @cert-authority entry
and all entries for hosts that don't support certificates. You can
also add any @revoked entries if you wish to.

```bash
    $ cat >>known_hosts_unhashed <<EOF
    # Hosts that do not support certificates
    edg.tocco.ch,edgtest.tocco.ch ssh-rsa AAAAB3NzaC1yc2E.............dsFisiXZGnqUAEl1Fdw==

    # Certificate authority
    @cert-authority *.tocco.ch ssh-rsa AAAAB3NzaC1yc2E.........RupUs+x83ncTR4Q== peter@pg
    EOF
```

## Generate known_hosts files.

```bash
    $ ./ssh_generate_known_hosts_files
    Original contents retained as known_hosts_hashed.old
    WARNING: known_hosts_hashed.old contains unhashed entries
    Delete this file to ensure privacy of hostnames
    known_hosts_full_hashed updated.
    Original contents retained as known_hosts_full_hashed.old
    WARNING: known_hosts_full_hashed.old contains unhashed entries
    Delete this file to ensure privacy of hostnames
```

This generates the following files:

* ``known_hosts_hashed``:
        Hashed version of known_hosts_hashed
* ``known_hosts_full_unhashed``:
        Content of known_hosts_unhashed and additionally entries for
        all hosts/keys for which certificates are issued.
* ``known_hosts_full_hashed``:
        Hashed version of known_hosts_full_unhashed. (Intended to be used
        for hosts that don't support certificates.)


## Automatically Created/Maintained Files

### Serial number of the last issued certificate
```bash
    $ cat serial
    31
```

### Issue date
```bash
    $ cat app01/issue_date
    2016-02-15T08:31:46Z
```

### Expiration date
```bash
    $ cat app01/expiration_date
    2016-08-13T08:31:45Z
```

