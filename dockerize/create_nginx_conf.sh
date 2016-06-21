#!/bin/bash

echo "What is your servers FQDN? "
read FQDN
echo "What is your servers IP? "
read IP_ADDR

cat <<EOF > nginx/b2share.conf
server {
        listen 80;
        server_name $FQDN;
        charset utf-8;
        
        location /oai2d {
                proxy_pass http://b2share:5000/oai2d;
                proxy_set_header Host $FQDN;
                proxy_set_header X-Real-IP $IP_ADDR;
                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }

        location / {
                proxy_pass https://b2share;
                proxy_set_header Host $FQDN;
                proxy_set_header X-Real-IP $IP_ADDR;
                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
                root /usr/share/nginx/html;
        }
}

server {
        listen 443 ssl;
        server_name $FQDN;
        charset utf-8;
        ssl_certificate         /etc/ssl/b2share.crt;
        ssl_certificate_key     /etc/ssl/b2share.key;
        ssl_protocols           TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers             HIGH:!aNULL:!MD5;

        location / {
                proxy_pass http://b2share:5000;
                proxy_set_header Host $FQDN;
                proxy_set_header X-Real-IP $IP_ADDR;
                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
                root /usr/share/nginx/html;
        }
}
EOF

if which openssl >/dev/null; then
	OPENSSL_BIN=`which openssl`
else
	echo "OpenSSL binary not found. Unable to create certificates."
	exit
fi
$OPENSSL_BIN genrsa -out nginx/b2share.key 2048
$OPENSSL_BIN req -new -key nginx/b2share.key -out nginx/b2share.csr
$OPENSSL_BIN req -x509 -days 365 -key nginx/b2share.key -in nginx/b2share.csr -out nginx/b2share.crt
