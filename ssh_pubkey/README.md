# SSH Certificate Authority Utilities

## Generate authorized_keys file

### Generate authorized_keys File for User tocco on Host app05
```bash
ssh-pubkey-parser auth ~/ssh_auth/f tocco@app05
```

### Remove Domain Part
```bash
ssh-pubkey-parser --domain tocco.ch auth public_keys_file tocco@app05.tocco.ch
```

## Generate YAML Lookup-Dictionary for ELK
```bash
ssh-pubkey-parser hash pubic_keys_file
```

## Further Options

Same as auth except that keys that don't have access are commented out instead
of simply left out.
```bash
ssh-pubkey-parser authall …
```
