#!/bin/bash

# ================================
# 🐧 SETUP RÁPIDO PARA LINUX MINT
# ================================
# Script optimizado para trabajar desde Linux Mint

set -e  # Salir si hay errores

echo "🐧 CONFIGURANDO SYSMEREI TF1 EN LINUX MINT"
echo "=========================================="

# Variables
PROJECT_NAME="SysMeReitF1"
PYTHON_VERSION="python3"

# 1. ACTUALIZAR SISTEMA
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. INSTALAR DEPENDENCIAS DEL SISTEMA
echo "🔧 Instalando dependencias del sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget \
    htop \
    build-essential \
    libssl-dev \
    libffi-dev \
    sqlite3

# 3. CREAR ENTORNO VIRTUAL
echo "🏠 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# 4. ACTUALIZAR PIP
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# 5. INSTALAR DEPENDENCIAS PYTHON
echo "📚 Instalando dependencias Python..."
pip install -r cloud_deployment/requirements.txt

# 6. CREAR DIRECTORIOS DE TRABAJO
echo "📁 Creando estructura de directorios..."
mkdir -p {logs,data,models,submissions,backups,config}

# 7. CONFIGURAR PERMISOS
echo "🔐 Configurando permisos..."
chmod +x cloud_deployment/aws_setup.sh
chmod 755 automatizacion/*.py
chmod 755 *.py

# 8. CREAR ARCHIVO DE CONFIGURACIÓN LOCAL
echo "⚙️ Creando configuración local..."
cat > .env << 'EOF'
# ================================
# 🐧 CONFIGURACIÓN PARA LINUX MINT
# ================================

# Configuración básica
DEBUG=True
ENVIRONMENT=development
BASE_DIR=$(pwd)

# Credenciales Kaggle (COMPLETAR)
KAGGLE_USERNAME=tu_usuario_kaggle
KAGGLE_KEY=tu_api_key_kaggle

# Configuración de competencia
COMPETITION_NAME=neuro-kup-ii-beta-acm-ai
MAX_SUBMISSIONS_PER_DAY=7
MIN_IMPROVEMENT_THRESHOLD=0.001

# Intervalos (más frecuentes para desarrollo)
TRAINING_INTERVAL_HOURS=2
VERIFICATION_INTERVAL_MINUTES=15

# Logging
LOG_LEVEL=DEBUG
LOG_MAX_BYTES=5242880
LOG_BACKUP_COUNT=3

# Monitoreo (ajustado para desarrollo)
HEALTH_CHECK_INTERVAL=180
MAX_MEMORY_MB=4096
MAX_CPU_PERCENT=85

# Notificaciones (deshabilitadas por defecto)
EMAIL_ENABLED=false
SLACK_ENABLED=false

# AWS (para cuando quieras desplegar)
S3_BACKUP_ENABLED=false
EOF

echo ""
echo "✅ INSTALACIÓN COMPLETADA"
echo "========================"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. 📝 Configurar credenciales de Kaggle:"
echo "   nano .env  # Editar KAGGLE_USERNAME y KAGGLE_KEY"
echo ""
echo "2. 📂 Colocar tus datasets:"
echo "   cp /ruta/a/train.csv data/"
echo "   cp /ruta/a/test_public.csv data/"
echo "   cp /ruta/a/test_private.csv data/"
echo ""
echo "3. 🚀 Activar entorno y probar:"
echo "   source venv/bin/activate"
echo "   python automatizacion/setup_completo.py"
echo ""
echo "4. 🧪 Ejecutar prueba básica:"
echo "   python ejemplo_uso_calcularf1.py"
echo ""
echo "5. 🤖 Iniciar sistema automático:"
echo "   python main_production.py"
echo ""
echo "6. ☁️ Para desplegar en AWS:"
echo "   cat cloud_deployment/DEPLOYMENT_GUIDE.md"
echo ""
echo "🎯 ¡El sistema está listo para competir en NeuroKup II!"
echo ""
echo "📊 Monitoreo en tiempo real:"
echo "   tail -f logs/neurokup.log"
echo ""
echo "🐧 Optimizado para Linux Mint - ¡Disfruta de la velocidad!"
