#!/usr/bin/env bash

# check if firectl installed
if [ -x "$(command -v firectl)" ]; then
  echo "firectl is already installed"
  exit 0
fi

# install
wget -O firectl.gz https://storage.googleapis.com/fireworks-public/firectl/stable/linux-amd64.gz
gunzip firectl.gz
sudo install -o root -g root -m 0755 firectl /usr/local/bin/firectl
