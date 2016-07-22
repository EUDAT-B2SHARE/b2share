FROM nginx
EXPOSE 80 443

RUN rm /etc/nginx/conf.d/*.conf
COPY b2share.conf /etc/nginx/conf.d/
COPY b2share.key /etc/ssl/
COPY b2share.crt /etc/ssl/

CMD ["nginx","-g","daemon off;"]
