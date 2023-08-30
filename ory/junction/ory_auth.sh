#!/bin/bash

/usr/bin/expect <<EOF
spawn ory auth
expect "Do you want to sign in to an existing Ory Network account?"
send -- "y\r"
expect "Email:"
send -- "${ORY_USERNAME}\r"
expect "Password:"
send -- "${ORY_PASSWORD}\r"
expect eof
EOF
