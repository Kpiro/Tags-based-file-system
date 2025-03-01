#!/bin/bash
ip route del default || true
ip route add default via 10.0.10.254
# Mantén el contenedor en ejecución sin hacer nada más
tail -f /dev/null