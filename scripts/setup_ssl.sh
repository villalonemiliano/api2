#!/bin/bash

# Exit on error
set -e

# Variables
DOMAIN="tu-dominio.com"
EMAIL="tu-email@dominio.com"
CERTBOT_PATH="/etc/letsencrypt/live/$DOMAIN"

# Instalar Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d $DOMAIN -m $EMAIL --agree-tos --non-interactive

# Configurar renovación automática
echo "0 0 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo tee -a /etc/cron.d/certbot-renew

# Verificar permisos
sudo chown -R root:root $CERTBOT_PATH
sudo chmod -R 755 $CERTBOT_PATH 