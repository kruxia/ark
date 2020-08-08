#!/bin/bash

# install git, direnv, docker, htpasswd
sudo apt-get update 
sudo apt-get install -y \
    git \
    direnv \
    apache2-utils \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install -y \
     docker-ce \
     docker-ce-cli \
     containerd.io

# install docker-compose
sudo curl -L \
    "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose

# hook direnv into the shell
echo 'eval "$(direnv hook bash)"' >>~/.bashrc

echo Creating a self-signed certificate to get started with
mkdir -p ui/ssl
openssl genrsa -des3 -passout pass:xxxxxxxx -out ui/ssl/server.key 2048
openssl rsa -passin pass:xxxxxxxx -in ui/ssl/server.key -out ui/ssl/server.key
openssl req -new -key ui/ssl/server.key -out ui/ssl/server.csr
openssl x509 -req -sha256 -days 365 -in ui/ssl/server.csr -signkey ui/ssl/server.key -out ui/ssl/server.crt

echo IMPORTANT: Replace this self-signed cert with one from a certificate authority A.S.A.P.

echo You must initialize the docker stack with 'docker stack init [ipaddress]'
echo and you must create an htpasswd file at ./ui/nginx/.htpasswd
echo then you can 'docker stack deploy -c deploy.docker-compose.yml ark'
