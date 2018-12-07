#!/bin/bash

set -x

sed -i "s/HBASE_IP/${HBASE_IP}/g" python.ini
sed -i "s/HBASE_PORT/${HBASE_PORT}/g" python.ini

sed -i "s/REDIS_IP:REDIS_PORT/${REDIS_IP}:${REDIS_PORT}/g" python.ini

python example_server.py
