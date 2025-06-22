#!/bin/bash

# ================================
# 🚀 UBUNTU 24.04 SETUP SCRIPT - NEUROKUP II
# ================================
# Script optimizado para Ubuntu 24.04 (Noble Numbat)

set -e  # Salir si hay errores

echo "🚀 CONFIGURANDO SISTEMA EN UBUNTU 24.04"
echo "======================================="

# Variables de configuración
PROJECT_DIR="/home/ubuntu/neurokup-system"
SERVICE_USER="neurokup"

# 1. ACTUALIZAR SISTEMA
echo "📦 Actualizando sistema..."
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. INSTALAR PYTHON Y DEPENDENCIAS DEL SISTEMA
echo "🐍 Instalando Python 3.12 y dependencias..."
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    python3-full \
    git \
    curl \
    wget \
    htop \
    supervisor \
    nginx \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    dos2unix \
    unzip

# 3. VERIFICAR INSTALACIÓN DE PYTHON
echo "🔍 Verificando Python..."
python3 --version
pip3 --version

# 4. CREAR USUARIO DEL SERVICIO
echo "👤 Creando usuario del servicio..."
if ! id "$SERVICE_USER" >/dev/null 2>&1; then
    sudo useradd -r -s /bin/false $SERVICE_USER
    echo "✅ Usuario $SERVICE_USER creado"
else
    echo "ℹ️ Usuario $SERVICE_USER ya existe"
fi

# 5. CREAR DIRECTORIO DEL PROYECTO
echo "📁 Creando directorio del proyecto..."
sudo mkdir -p $PROJECT_DIR
sudo chown ubuntu:ubuntu $PROJECT_DIR

# 6. CLONAR REPOSITORIO
echo "📥 Clonando repositorio..."
cd $PROJECT_DIR
if [ ! -d ".git" ]; then
    git clone https://github.com/Jos3phil/SysMeReitF1.git
else
    git pull origin main
fi

# 7. CREAR ENTORNO VIRTUAL
echo "🏗️ Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# 8. ACTUALIZAR PIP Y SETUPTOOLS
echo "⬆️ Actualizando pip..."
pip install --upgrade pip setuptools wheel

# 9. INSTALAR DEPENDENCIAS PYTHON
echo "📦 Instalando dependencias Python..."
# Instalar las dependencias principales sin versiones específicas para compatibilidad con Python 3.12
pip install \
    pandas \
    numpy \
    scikit-learn \
    xgboost \
    lightgbm \
    requests \
    flask \
    python-dotenv \
    schedule \
    psutil \
    fastapi \
    uvicorn

# 10. CONFIGURAR VARIABLES DE ENTORNO
echo "⚙️ Configurando variables de entorno..."
cat > $PROJECT_DIR/.env << EOF
# Configuración de producción
ENVIRONMENT=production
PROJECT_DIR=$PROJECT_DIR
LOG_LEVEL=INFO
API_PORT=8000

# Configuración de competencia
COMPETITION_URL=tu_url_de_competencia
TEAM_TOKEN=tu_token_aqui

# Configuración de modelos
MODEL_DIR=$PROJECT_DIR/models
DATA_DIR=$PROJECT_DIR/data
RESULTS_DIR=$PROJECT_DIR/resultados
EOF

# 11. CONFIGURAR PERMISOS
echo "🔐 Configurando permisos..."
sudo chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
sudo chmod +x $PROJECT_DIR/cloud_deployment/*.sh

# 12. CONFIGURAR SUPERVISOR
echo "⚙️ Configurando supervisor..."
sudo tee /etc/supervisor/conf.d/neurokup.conf > /dev/null << EOF
[program:neurokup-system]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/cloud_deployment/main.py
directory=$PROJECT_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
stderr_logfile=/var/log/neurokup-error.log
stdout_logfile=/var/log/neurokup-access.log
environment=PATH="$PROJECT_DIR/venv/bin"
EOF

# 13. CONFIGURAR NGINX
echo "🌐 Configurando nginx..."
sudo tee /etc/nginx/sites-available/neurokup > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/neurokup /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 14. CREAR ESTRUCTURA DE DIRECTORIOS
echo "📂 Creando estructura de directorios..."
mkdir -p $PROJECT_DIR/{logs,models,data,resultados,backups}

# 15. CREAR SCRIPTS DE UTILIDAD
echo "🛠️ Creando scripts de utilidad..."

# Script de inicio
cat > $PROJECT_DIR/start_system.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/neurokup-system
source venv/bin/activate
python cloud_deployment/main.py
EOF
chmod +x $PROJECT_DIR/start_system.sh

# Script de status
cat > $PROJECT_DIR/check_status.sh << 'EOF'
#!/bin/bash
echo "=== ESTADO DEL SISTEMA ==="
echo "Supervisor status:"
sudo supervisorctl status
echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager -l
echo ""
echo "Logs recientes:"
tail -n 20 /var/log/neurokup-access.log
EOF
chmod +x $PROJECT_DIR/check_status.sh

# 16. INICIAR SERVICIOS
echo "🚀 Iniciando servicios..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start neurokup-system

sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# 17. CONFIGURAR FIREWALL
echo "🔥 Configurando firewall..."
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw --force enable

# 18. VERIFICACIÓN FINAL
echo "✅ INSTALACIÓN COMPLETADA!"
echo "=========================="
echo "📍 Directorio del proyecto: $PROJECT_DIR"
echo "🌐 URL: http://$(curl -s ifconfig.me)"
echo ""
echo "📋 COMANDOS ÚTILES:"
echo "  • Ver logs: sudo tail -f /var/log/neurokup-*.log"
echo "  • Estado: sudo supervisorctl status"
echo "  • Reiniciar: sudo supervisorctl restart neurokup-system"
echo "  • Status completo: $PROJECT_DIR/check_status.sh"
echo ""
echo "🔍 Verificando estado actual..."
$PROJECT_DIR/check_status.sh

echo ""
echo "🎉 ¡Sistema listo para usar!"
