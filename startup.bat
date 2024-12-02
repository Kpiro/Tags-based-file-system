@echo off

echo "Creando redes..."
docker network create clients --subnet 10.0.10.0/24
if %ERRORLEVEL% neq 0 (
    echo Error creating clients networks.
    exit /b 1
)
docker network create servers --subnet 10.0.11.0/24
if %ERRORLEVEL% neq 0 (
    echo Error creating servers networks.
    exit /b 1
)

echo "Construyendo la imagen del router..."
docker build -t router-image -f Router/Dockerfile.router .
if %ERRORLEVEL% neq 0 (
    echo Error building router image.
    exit /b 1
)

echo "Creando y configurando el router..."
docker run -itd --rm --name router router-image
if %ERRORLEVEL% neq 0 (
    echo Error creating and configurating router.
    exit /b 1
)
docker network connect --ip 10.0.10.254 clients router
if %ERRORLEVEL% neq 0 (
    echo Error connecting router to clients network.
    exit /b 1
)
docker network connect --ip 10.0.11.254 servers router
if %ERRORLEVEL% neq 0 (
    echo Error connecting router to servers network.
    exit /b 1
)

echo "Construyendo las imágenes de cliente y servidor..."
docker build -t client -f Client/Dockerfile.client .
if %ERRORLEVEL% neq 0 (
    echo Error building client image.
    exit /b 1
)
docker build -t server -f Server/Dockerfile.server .
if %ERRORLEVEL% neq 0 (
    echo Error building server image.
    exit /b 1
)

echo "Startup completado."

echo "Iniciando el servidor..."
docker run -d --name server1 --cap-add NET_ADMIN --network servers server
if %ERRORLEVEL% neq 0 (
    echo Error starting server container.
    exit /b 1
)

echo "Iniciando los clientes..."
docker run -it -v /d:/app/Client/client_files --name client1 --cap-add NET_ADMIN --network clients client
if %ERRORLEVEL% neq 0 (
    echo Error starting client1 container.
    exit /b 1
)

docker run -it -v /d:/app/Client/client_files --name client2 --cap-add NET_ADMIN --network clients client
if %ERRORLEVEL% neq 0 (
    echo Error starting client2 container.
    exit /b 1
)

docker run -it -v /d:/app/Client/client_files --name client3 --cap-add NET_ADMIN --network clients client
if %ERRORLEVEL% neq 0 (
    echo Error starting client3 container.
    exit /b 1
)
pause