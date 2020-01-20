#!/usr/bin/env bash

if [ ! -f localhost.crt ] ||  [ ! -f localhost.key ]; then
  echo "Generating self-signed certs for localhost"
  openssl req -x509 -out localhost.crt -keyout localhost.key \
    -newkey rsa:2048 -nodes -sha256 \
    -subj '/CN=localhost' -extensions EXT -config <( \
     printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
fi

exec gunicorn --bind=0.0.0.0:8443 --certfile=localhost.crt --keyfile=localhost.key datalog_analyser.app:APP
