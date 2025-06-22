#!/bin/bash

# ================================
# 🚀 AWS EC2 SETUP SCRIPT - NEUROKUP II
# ================================
# Script para configurar el sistema en AWS EC2 Ubuntu

set -e  # Salir si hay errores

# Corregir terminaciones de línea si es necesario
if command -v dos2unix >/dev/null 2>&1; then
    dos2unix "$0" 2>/dev/null || true
fi

echo "🚀 CONFIGURANDO SISTEMA EN AWS EC2"
echo "=================================="

# Variables de configuración
PROJECT_DIR="/home/ubuntu/neurokup-system"
SERVICE_USER="neurokup"

# Detectar versión de Ubuntu y Python disponible
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2 || echo "3.12")

echo "🐧 Ubuntu version: $UBUNTU_VERSION"
echo "🐍 Python version available: $PYTHON_VERSION"

# 1. ACTUALIZAR SISTEMA
echo "📦 Actualizando sistema..."
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. INSTALAR PYTHON Y DEPENDENCIAS DEL SISTEMA
echo "🐍 Instalando Python y dependencias..."

# Para Ubuntu 24.04 (Noble) usamos python3 por defecto
if [[ "$UBUNTU_VERSION" == "24.04" || "$PYTHON_VERSION" == "3.12" ]]; then
    echo "📋 Detectado Ubuntu 24.04 - usando Python 3.12"
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
        software-properties-common \
        unzip
else
    echo "📋 Detectado Ubuntu anterior - intentando Python 3.9"
    sudo apt-get install -y \
        python3.9 \
        python3.9-venv \
        python3.9-dev \
        python3-pip \
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
        software-properties-common
fi

# 3. CREAR USUARIO DEL SERVICIO
echo "👤 Creando usuario del servicio..."
sudo useradd -m -s /bin/bash $SERVICE_USER || echo "Usuario ya existe"

# 4. CREAR DIRECTORIO DEL PROYECTO
echo "📁 Creando estructura de directorios..."
sudo mkdir -p $PROJECT_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

# 5. CONFIGURAR ENTORNO VIRTUAL
echo "🏠 Configurando entorno virtual..."

# Determinar comando Python correcto
if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_CMD="python3.12"
elif command -v python3.9 >/dev/null 2>&1; then
    PYTHON_CMD="python3.9"
else
    PYTHON_CMD="python3"
fi

echo "🐍 Usando comando Python: $PYTHON_CMD"

sudo -u $SERVICE_USER $PYTHON_CMD -m venv $PROJECT_DIR/venv
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip

# 6. INSTALAR DEPENDENCIAS PYTHON
echo "📚 Instalando dependencias Python..."
echo "⏳ Esto puede tomar varios minutos..."

# Actualizar pip y setuptools primero
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip setuptools wheel

# Instalar dependencias principales (sin versiones específicas para Python 3.12)
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install \
    pandas \
    numpy \
    scikit-learn \
    xgboost \
    lightgbm \
    requests \
    schedule \
    imbalanced-learn \
    psutil \
    python-dotenv

# Instalar dependencias opcionales (que pueden fallar sin romper el sistema)
echo "📦 Instalando dependencias opcionales..."
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install matplotlib seaborn jupyter kaggle || echo "⚠️ Algunas dependencias opcionales fallaron pero el sistema funcionará"

# 7. CREAR DIRECTORIOS DE TRABAJO
echo "📂 Creando directorios de trabajo..."
sudo -u $SERVICE_USER mkdir -p $PROJECT_DIR/{logs,data,models,submissions,config,backups}

# 8. CONFIGURAR PERMISOS
echo "🔐 Configurando permisos..."
sudo chmod 755 $PROJECT_DIR
sudo chmod 750 $PROJECT_DIR/{logs,data,models,submissions,config,backups}

# 9. CONFIGURAR LOGROTATE
echo "📝 Configurando rotación de logs..."
sudo tee /etc/logrotate.d/neurokup << EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $SERVICE_USER $SERVICE_USER
}
EOF

# 10. CONFIGURAR SUPERVISOR
echo "👮 Configurando supervisor..."
sudo tee /etc/supervisor/conf.d/neurokup.conf << EOF
[program:neurokup-automation]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py
directory=$PROJECT_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/supervisor_error.log
stdout_logfile=$PROJECT_DIR/logs/supervisor_output.log
environment=PYTHONPATH="$PROJECT_DIR"
EOF

# 11. CONFIGURAR FIREWALL BÁSICO
echo "🔥 Configurando firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=================================="
echo "📌 Próximos pasos:"
echo "1. Copiar código del proyecto a $PROJECT_DIR"
echo "2. Configurar variables de entorno en $PROJECT_DIR/.env"
echo "3. Reiniciar supervisor: sudo supervisorctl reread && sudo supervisorctl update"
echo "4. Verificar estado: sudo supervisorctl status"
