FROM bitnami/python:3.6.7
LABEL Author="wangrui<cfwr1991@126.com>"

ENV REDIS_IP REDIS_IP
ENV REDIS_PORT REDIS_PORT

ENV HBASE_IP HBASE_IP
ENV HBASE_PORT HBASE_PORT

COPY trend /service/trend
WORKDIR /service/trend/src

ADD start.sh /service/trend/src
RUN chmod -R 777 /service/trend/src/start.sh

RUN pip install -r /service/trend/src/requirements.txt

CMD ["/service/trend/src/start.sh"]

ENTRYPOINT tail -f /dev/null
