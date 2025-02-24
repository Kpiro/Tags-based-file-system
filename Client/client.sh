#!/bin/bash
ip route del default || true
ip route add default via 10.0.10.254
python /app/Client/client.py