#!/bin/bash
ip route del default || true
ip route add default via 10.0.11.254
python /app/Server/server.py