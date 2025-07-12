# Script para configurar el firewall de Azure SQL
# Ejecutar en Azure CLI

# Permitir acceso desde cualquier IP (para Railway)
az sql server firewall-rule create \
    --resource-group SSVQ \
    --server ssvq \
    --name AllowAllIps \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 255.255.255.255

# Permitir servicios de Azure
az sql server firewall-rule create \
    --resource-group SSVQ \
    --server ssvq \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
