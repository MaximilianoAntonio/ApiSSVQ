#!/bin/bash
# Script para verificar que la API esté funcionando en HTTPS

echo "Verificando API en HTTPS..."
curl -I https://web-production-5e000.up.railway.app/api/conductores/

echo -e "\n\nVerificando redirection HTTP -> HTTPS..."
curl -I http://web-production-5e000.up.railway.app/api/conductores/

echo -e "\n\nSi ves 'HTTP/2 200' o redirección 301/302 a HTTPS, está funcionando correctamente."
