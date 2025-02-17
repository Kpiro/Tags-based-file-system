#!/bin/bash

set -e  # Habilita la detención en caso de error

echo "Eliminando contenedores existentes si existen..."
docker rm -f router 2>/dev/null || true
docker rm -f server1 2>/dev/null || true
docker rm -f server2 2>/dev/null || true
docker rm -f server3 2>/dev/null || true
docker rm -f server4 2>/dev/null || true
docker rm -f client1 2>/dev/null || true
docker rm -f client2 2>/dev/null || true
docker rm -f client3 2>/dev/null || true

echo "Eliminando imágenes existentes si existen..."
docker rmi -f router-image 2>/dev/null || true
docker rmi -f router:base 2>/dev/null || true
docker rmi -f client 2>/dev/null || true
docker rmi -f server 2>/dev/null || true

echo "Eliminando redes existentes si existen..."
docker network rm clients 2>/dev/null || true
docker network rm servers 2>/dev/null || true

echo "Creando redes..."
docker network create clients --subnet 10.0.10.0/24 || { echo "Error creating clients network." ; exit 1; }
docker network create servers --subnet 10.0.11.0/24 || { echo "Error creating servers network." ; exit 1; }

echo "Construyendo la imagen base del router..."
docker build -t router:base -f Router/router_base.Dockerfile . || { echo "Error building router base image." ; exit 1; }

echo "Construyendo la imagen del router..."
docker build -t router-image -f Router/router.Dockerfile . || { echo "Error building router image." ; exit 1; }

echo "Creando y configurando el router..."
docker run -d --rm --name router --cap-add NET_ADMIN -e PYTHONUNBUFFERED=1 router-image || { echo "Error creating and configuring router." ; exit 1; }
docker network connect --ip 10.0.10.254 clients router || { echo "Error connecting router to clients network." ; exit 1; }
docker network connect --ip 10.0.11.254 servers router || { echo "Error connecting router to servers network." ; exit 1; }

echo "Ejecutando container mcproxy..."
docker run -d --rm --name mcproxy --cap-add NET_ADMIN -e PYTHONUNBUFFERED=1 router-image || { echo "Error executing container mcproxy" ; exit 1; }

echo "Conectado contenedor del router a las redes cliente y servidor..."
docker network connect --ip 10.0.11.253 servers mcproxy || { echo "Error connecting container router to servers network." ; exit 1; }
docker network connect --ip 10.0.10.253 clients mcproxy || { echo "Error connecting container router to clients network." ; exit 1; }

echo "Construyendo las imágenes de cliente y servidor..."
docker build -t client -f Client/Dockerfile.client . || { echo "Error building client image." ; exit 1; }
docker build -t server -f Server/Dockerfile.server . || { echo "Error building server image." ; exit 1; }

echo "Startup completado."

echo "Iniciando los servidores..."
docker run -d \
  --name server1 \
  --cap-add NET_ADMIN \
  --network servers \
  -v "$(pwd)":/app \
  server || { echo "Error starting server container." ; exit 1; }

docker run -d \
  --name server2 \
  --cap-add NET_ADMIN \
  --network servers \
  -v "$(pwd)":/app \
  server || { echo "Error starting server container." ; exit 1; }

docker run -d \
  --name server3 \
  --cap-add NET_ADMIN \
  --network servers \
  -v "$(pwd)":/app \
  server || { echo "Error starting server container." ; exit 1; }

docker run -d \
  --name server4 \
  --cap-add NET_ADMIN \
  --network servers \
  -v "$(pwd)":/app \
  server || { echo "Error starting server container." ; exit 1; }

echo "Iniciando los clientes..."
docker run -d \
  --name client1 \
  --cap-add NET_ADMIN \
  --network clients \
  -v "$(pwd)":/app \
  client || { echo "Error starting client1 container." ; exit 1; }
docker run -d \
  --name client2 \
  --cap-add NET_ADMIN \
  --network clients \
  -v "$(pwd)":/app \
  client || { echo "Error starting client2 container." ; exit 1; }
docker run -d \
  --name client3 \
  --cap-add NET_ADMIN \
  --network clients \
  -v "$(pwd)":/app \
  client || { echo "Error starting client3 container." ; exit 1; }

echo "Proceso finalizado con éxito."
