# cacert

A simple role to copy a cacert into place and make it trusted on debian machines.
Set to variables:

- cert_src - the path to the cert to copy
- cert_name - the name of the cert on the remote system. Note that it must end in a .crt extension.
