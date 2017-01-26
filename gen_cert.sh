#!/bin/bash

# Thanks to https://www.jamescoyle.net/how-to/1073-bash-script-to-create-an-ssl-certificate-key-and-request-csr

domain=eva.local
commonname=eva.local
country=CA
state=Ontario
locality=Ottawa
organization=Eva
organizationalunit=IT
email=admin@eva.local
password='password'
path=`realpath $0`
dir=`dirname $path`

# Generate a key
openssl genrsa -des3 -passout pass:$password -out $dir/$domain.key 2048 -noout
# Remove passphrase from the key. Comment the line out to keep the passphrase
openssl rsa -in $dir/$domain.key -passin pass:$password -out $dir/$domain.key
# Create the request
openssl req -new -key $dir/$domain.key -out $dir/$domain.csr -passin pass:$password \
    -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
# Create the Cert
openssl x509 -req -days 3650 -in $dir/$domain.csr -signkey $dir/$domain.key -out $dir/$domain.crt
