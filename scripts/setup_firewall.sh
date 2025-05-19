#!/bin/bash

# Exit on error
set -e

# Reset UFW
sudo ufw --force reset

# Política por defecto
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (cambia el puerto si usas uno diferente)
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir el puerto de la API (solo desde localhost)
sudo ufw allow from 127.0.0.1 to any port 5002

# Habilitar UFW
sudo ufw --force enable

# Verificar estado
sudo ufw status verbose

# Configurar logging
sudo ufw logging on
sudo ufw logging high

# Crear directorio de logs si no existe
sudo mkdir -p /var/log/ufw
sudo chown -R root:root /var/log/ufw
sudo chmod -R 755 /var/log/ufw

# Configurar rotación de logs
sudo tee /etc/logrotate.d/ufw << EOF
/var/log/ufw.log
{
    rotate 7
    daily
    missingok
    notifempty
    compress
    delaycompress
    sharedscripts
    postrotate
        /usr/sbin/ufw status > /dev/null 2>&1 || true
    endscript
}
EOF 