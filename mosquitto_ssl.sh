#!/bin/bash

wd="`dirname $0`"
if [ ! -z "$wd" ]; then
    if [ $wd == "." ];then wd=`pwd`;fi  
fi

certDir="${wd}/certs";
conf_dir="/mosquitto/config" #WD

rm -rf ${certDir} 

mkdir -p ${certDir}

cd ${certDir}


#subjectAltName olmazsa self signet sertifika ile bağlanamıyor.
#Server IP - Port bilgileri

#~ IP="mqtt.eclipseprojects.io"

IP="192.168.1.10"
PORT="58883"

SUBJECT_CA="/C=TR/ST=Istanbul/L=Istanbul/O=Example/OU=CA/CN=$IP"
SUBJECT_SERVER="/C=TR/ST=Istanbul/L=Istanbul/O=Example/OU=server/CN=$IP"
SUBJECT_CLIENT="/C=TR/ST=Istanbul/L=Istanbul/O=Example/OU=client/CN=$IP"

MAX_DAYS=3650
 
SB_NAME="subjectAltName = IP:127.0.0.1" #"subjectAltName=DNS:example.com,IP:$IP"
space="################################################################################################################"

function generate_CA () {
   echo -e "$SUBJECT_CA\n$space" 
   openssl req -x509 -nodes -sha256 -newkey rsa:2048 -subj "$SUBJECT_CA" -addext  "${SB_NAME}" -days ${MAX_DAYS} -keyout ca.key -out ca.crt 
   
}

function generate_server () {
    echo -e "$SUBJECT_SERVER\n$space"

    openssl req -nodes -sha256 -new -subj "$SUBJECT_SERVER" -keyout server.key -out server.csr -addext "${SB_NAME}"

    openssl x509 -req -in server.csr \
    -extfile <(printf "${SB_NAME}") \
    -CA ca.crt \
    -CAkey ca.key \
    -CAcreateserial -out server.crt \
    -days ${MAX_DAYS}
}

function generate_client () {
   echo -e "$SUBJECT_CLIENT\n$space"
   openssl req -new -nodes -sha256 -subj "$SUBJECT_CLIENT" -out client.csr -keyout client.key 
   openssl x509 -req -sha256 -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days ${MAX_DAYS}
}

function clean () {
   echo -e "$SUBJECT_CLIENT\n$space"
    rm client.csr client.key client.crt 
    rm server.csr server.key server.crt 
    rm ca.srl ca.key ca.crt 
}


#~ clean

generate_CA
generate_server
generate_client
############################################
cd ${wd}

echo "port ${PORT}

#require_certificate true

cafile ${conf_dir}/certs/ca.crt
certfile ${conf_dir}/certs/server.crt
keyfile ${conf_dir}/certs/server.key

tls_version tlsv1.2

use_identity_as_username true
password_file ${conf_dir}/password.txt
listener 1883

persistence false
persistence_location /mosquitto/data/

" > mosquitto.conf



echo "Use Examples
#Server

mosquitto -c ${certDir}/mosquitto.conf -v

#Subcriber

mosquitto_sub -h ${IP} -p ${PORT}  --cafile ${certDir}/ca.crt --cert ${certDir}/client.crt --key ${certDir}/client.key -t temperature

#Publisher
