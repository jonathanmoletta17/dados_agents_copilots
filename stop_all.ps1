Write-Host "Stopping SIS Smart Search..."
cd sis-smart-search
docker-compose down
cd ..

Write-Host "Stopping GLPI Smart Search..."
cd glpi-smart-search
docker-compose down
cd ..

Write-Host "Stopping SIS Carregadores Dashboard..."
cd 06.1.1-sis-carregadores-dashboard
docker-compose down
cd ..

Write-Host "Stopping SIS Dashboard..."
cd 06.1-sis-dashboard
docker-compose down
cd ..

Write-Host "Stopping DTIC Dashboard..."
cd 06-dtic-dashboard
docker-compose down
cd ..

Write-Host "Stopping GLPI Data Service..."
cd glpi-data-service
docker-compose down
cd ..

Write-Host "All services stopped!"
