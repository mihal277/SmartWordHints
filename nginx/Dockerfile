FROM nginx:1.19.6

RUN useradd --create-home -u 5001 smart-word-hints-nginx
USER smart-word-hints-nginx

RUN mkdir /tmp/nginx

COPY --chown=5001:5001 fullchain.pem /home/smart-word-hints-nginx/fullchain.pem
COPY --chown=5001:5001 privkey.pem /home/smart-word-hints-nginx/privkey.pem

COPY nginx.conf /etc/nginx/nginx.conf
