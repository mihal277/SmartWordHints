FROM nginx:1.19.6

RUN useradd --create-home -u 5001 smart_word_hints_nginx
USER smart_word_hints_nginx

RUN mkdir /tmp/nginx

COPY --chown=5001:5001 fullchain.pem /home/smart_word_hints_nginx/fullchain.pem
COPY --chown=5001:5001 privkey.pem /home/smart_word_hints_nginx/privkey.pem

COPY nginx.conf /etc/nginx/nginx.conf
