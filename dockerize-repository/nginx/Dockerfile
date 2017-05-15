FROM nginx:1.11
EXPOSE 80 443

RUN rm /etc/nginx/conf.d/*.conf
RUN mkdir -p /etc/ssl/
RUN openssl genrsa -out /etc/ssl/b2share.key 2048
RUN openssl req -new -key /etc/ssl/b2share.key -out /etc/ssl/b2share.csr -subj "/C=CH/ST=Geneva/L=Geneva/O=B2Share Test Certificate/OU=B2Share/CN=example.com"
RUN openssl req -x509 -days 365 -key /etc/ssl/b2share.key -in /etc/ssl/b2share.csr -out /etc/ssl/b2share.crt
COPY b2share.conf /etc/nginx/conf.d/

CMD ["nginx","-g","daemon off;"]
