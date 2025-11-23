Write-Host "Starting GLPI Data Service (Database & Core)..."
cd glpi-data-service
docker-compose up -d --build
cd ..

Write-Host "Starting DTIC Dashboard..."
cd 06-dtic-dashboard
docker-compose up -d --build
cd ..

Write-Host "Starting SIS Dashboard..."
cd 06.1-sis-dashboard
docker-compose up -d --build
cd ..

Write-Host "Starting SIS Carregadores Dashboard..."
cd 06.1.1-sis-carregadores-dashboard
docker-compose up -d --build
cd ..

Write-Host "Starting GLPI Smart Search..."
cd glpi-smart-search
docker-compose up -d --build
cd ..

Write-Host "Starting SIS Smart Search..."
cd sis-smart-search
docker-compose up -d --build
cd ..

Write-Host "All services started!"
