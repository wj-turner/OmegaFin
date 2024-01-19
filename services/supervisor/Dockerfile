FROM ubuntu
RUN apt-get update && apt-get install -y supervisor
COPY ./conf.d /etc/supervisor/conf.d
CMD ["/usr/bin/supervisord"]