#!/bin/bash -eu

OPENSSL_VER=3.2.0

mkdir openssl
cd openssl
wget https://www.openssl.org/source/openssl-${OPENSSL_VER}.tar.gz
tar xf openssl-${OPENSSL_VER}.tar.gz
cd openssl-${OPENSSL_VER}
./config zlib shared no-ssl3
make -j4
sudo make install
ldconfig /usr/local/lib64/

cd ../../
