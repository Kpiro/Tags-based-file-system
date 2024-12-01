@echo off

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not installed. Please install it before continuing.
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker Compose is not installed. Please install it before continuing.
    exit /b 1
)

echo Building the router image...
docker build -t router-image -f Router/Dockerfile.router .
if %ERRORLEVEL% neq 0 (
    echo Error building the router image.
    exit /b 1
)

echo Building the server image...
docker build -t server-image -f Server/Dockerfile.server .
if %ERRORLEVEL% neq 0 (
    echo Error building the server image.
    exit /b 1
)

echo Building the client image...
docker build -t client-image -f Client/Dockerfile.client .
if %ERRORLEVEL% neq 0 (
    echo Error building the client image.
    exit /b 1
)

echo Starting the containers with Docker Compose...
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo Error starting the containers with Docker Compose.
    exit /b 1
)

echo The network has been successfully set up.
pause