#!/bin/bash

# Exit on error
set -e

# Crear directorios de logs
sudo mkdir -p /var/log/stock_api
sudo chown -R root:root /var/log/stock_api
sudo chmod -R 755 /var/log/stock_api

# Configurar logrotate para la API
sudo tee /etc/logrotate.d/stock_api << EOF
/var/log/stock_api/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload nginx
        systemctl reload stock_api
    endscript
}
EOF

# Configurar rsyslog para centralizar logs
sudo tee /etc/rsyslog.d/30-stock_api.conf << EOF
# Logs de la API
if \$programname == 'stock_api' then /var/log/stock_api/api.log
if \$programname == 'stock_api' then stop

# Logs de Nginx
if \$programname == 'nginx' then /var/log/stock_api/nginx.log
if \$programname == 'nginx' then stop

# Logs de Gunicorn
if \$programname == 'gunicorn' then /var/log/stock_api/gunicorn.log
if \$programname == 'gunicorn' then stop
EOF

# Configurar monitoreo de logs
sudo tee /etc/logwatch/conf/logwatch.conf << EOF
LogDir = /var/log/stock_api
Output = mail
Format = html
MailTo = admin@tu-dominio.com
Range = yesterday
Detail = High
EOF

# Instalar herramientas de monitoreo
sudo apt-get update
sudo apt-get install -y logwatch fail2ban

# Configurar fail2ban para la API
sudo tee /etc/fail2ban/jail.d/stock_api.conf << EOF
[stock_api]
enabled = true
port = http,https
filter = stock_api
logpath = /var/log/stock_api/api.log
maxretry = 5
findtime = 600
bantime = 3600
EOF

# Crear filtro para fail2ban
sudo tee /etc/fail2ban/filter.d/stock_api.conf << EOF
[Definition]
failregex = ^.*Failed login attempt from <HOST>.*$
            ^.*Invalid API key from <HOST>.*$
            ^.*Rate limit exceeded from <HOST>.*$
ignoreregex =
EOF

# Reiniciar servicios
sudo systemctl restart rsyslog
sudo systemctl restart fail2ban

# Verificar configuración
sudo logrotate -d /etc/logrotate.d/stock_api
sudo fail2ban-client status stock_api 