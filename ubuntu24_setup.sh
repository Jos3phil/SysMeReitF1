#!/bin/bash

# ================================
# 🚀 INSTALACIÓN RÁPIDA UBUNTU 24.04
# ================================
# Script optimizado para Ubuntu 24.04 Noble

set -e

echo "🚀 INSTALACIÓN RÁPIDA NEUROKUP II - UBUNTU 24.04"
echo "================================================"

# Variables
PROJECT_DIR="/home/ubuntu/neurokup-system"
SERVICE_USER="neurokup"

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update -y

# 2. Instalar dependencias básicas
echo "🔧 Instalando dependencias del sistema..."
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    git \
    curl \
    wget \
    htop \
    build-essential \
    libssl-dev \
    libffi-dev \
    dos2unix \
    supervisor

# 3. Crear usuario y directorios
echo "👤 Configurando usuario y directorios..."
sudo useradd -m -s /bin/bash $SERVICE_USER 2>/dev/null || echo "Usuario ya existe"
sudo mkdir -p $PROJECT_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

# 4. Crear entorno virtual
echo "🐍 Configurando entorno virtual..."
sudo -u $SERVICE_USER python3 -m venv $PROJECT_DIR/venv
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip

# 5. Crear directorios de trabajo
echo "📁 Creando estructura de directorios..."
sudo -u $SERVICE_USER mkdir -p $PROJECT_DIR/{logs,data,models,submissions,config,backups}

# 6. Instalar dependencias Python básicas
echo "📚 Instalando dependencias Python básicas..."
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install \
    pandas \
    numpy \
    scikit-learn \
    requests \
    kaggle

# 7. Configurar permisos
echo "🔐 Configurando permisos..."
sudo chmod 755 $PROJECT_DIR
sudo chmod 750 $PROJECT_DIR/{logs,data,models,submissions,config,backups}

# 8. Crear archivo de configuración básico
echo "⚙️ Creando configuración básica..."
sudo -u $SERVICE_USER tee $PROJECT_DIR/.env << 'EOF'
# Configuración básica
DEBUG=False
ENVIRONMENT=production
BASE_DIR=/home/ubuntu/neurokup-system

# Credenciales Kaggle (COMPLETAR)
KAGGLE_USERNAME=tu_usuario_kaggle
KAGGLE_KEY=tu_api_key_kaggle

# Configuración de competencia
COMPETITION_NAME=neuro-kup-ii-beta-acm-ai
MAX_SUBMISSIONS_PER_DAY=7
MIN_IMPROVEMENT_THRESHOLD=0.001

# Intervalos
TRAINING_INTERVAL_HOURS=4
VERIFICATION_INTERVAL_MINUTES=30

# Logging
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ INSTALACIÓN BÁSICA COMPLETADA"
echo "================================"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. 📥 Clonar el repositorio:"
echo "   cd $PROJECT_DIR"
echo "   sudo -u $SERVICE_USER git clone https://github.com/Jos3phil/SysMeReitF1.git ."
echo ""
echo "2. 📝 Configurar credenciales de Kaggle:"
echo "   sudo nano $PROJECT_DIR/.env"
echo "   # Editar KAGGLE_USERNAME y KAGGLE_KEY"
echo ""
echo "3. 📚 Instalar dependencias completas:"
echo "   sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install -r cloud_deployment/requirements.txt"
echo ""
echo "4. 🚀 Probar el sistema:"
echo "   sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/python main_production.py"
echo ""
echo "🎯 Sistema listo para Ubuntu 24.04!"
