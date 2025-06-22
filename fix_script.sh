#!/bin/bash

# ================================
# 🔧 CORRECCIÓN DIRECTA EN AWS EC2 - NEUROKUP II
# ================================
# Ejecuta estos comandos directamente en AWS Ubuntu 24.04

echo "🔧 SOLUCIONANDO PROBLEMA DE TERMINACIONES DE LÍNEA..."
echo "🖥️ Detectado: Ubuntu 24.04 (Noble)"

# 1. ACTUALIZAR SISTEMA E INSTALAR HERRAMIENTAS
echo "📦 Instalando herramientas necesarias..."
sudo apt-get update -q
sudo apt-get install -y dos2unix curl wget

# 2. CREAR SCRIPT AWS_SETUP.SH DIRECTAMENTE
echo "📝 Creando aws_setup.sh con terminaciones Unix..."
cat > aws_setup.sh << 'SCRIPT_END'
#!/bin/bash

set -e

echo "🚀 CONFIGURANDO SISTEMA EN AWS EC2 - Ubuntu 24.04"
echo "================================================="

PROJECT_DIR="/home/ubuntu/neurokup-system"
SERVICE_USER="neurokup"

echo "📦 Actualizando sistema..."
sudo apt-get update -y

echo "🐍 Instalando Python y dependencias..."
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    git \
    curl \
    wget \
    htop \
    supervisor \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    dos2unix

echo "👤 Creando usuario del servicio..."
sudo useradd -m -s /bin/bash $SERVICE_USER 2>/dev/null || echo "Usuario ya existe"

echo "📁 Creando estructura de directorios..."
sudo mkdir -p $PROJECT_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

echo "🏠 Configurando entorno virtual..."
sudo -u $SERVICE_USER python3 -m venv $PROJECT_DIR/venv
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip

echo "📚 Instalando dependencias Python..."
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install \
    pandas \
    numpy \
    scikit-learn \
    matplotlib \
    seaborn \
    requests \
    schedule \
    imbalanced-learn \
    xgboost \
    lightgbm \
    kaggle \
    psutil \
    python-dotenv

echo "� Creando directorios de trabajo..."
sudo -u $SERVICE_USER mkdir -p $PROJECT_DIR/{logs,data,models,submissions,config,backups}

echo "🔐 Configurando permisos..."
sudo chmod 755 $PROJECT_DIR
sudo chmod 750 $PROJECT_DIR/{logs,data,models,submissions,config,backups}

echo "📝 Configurando rotación de logs..."
sudo tee /etc/logrotate.d/neurokup > /dev/null << EOF
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

echo "👮 Configurando supervisor..."
sudo tee /etc/supervisor/conf.d/neurokup.conf > /dev/null << EOF
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

echo "🔥 Configurando firewall básico..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

echo ""
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=========================="
echo "📌 Próximos pasos:"
echo "1. Clonar repositorio: git clone https://github.com/Jos3phil/SysMeReitF1.git $PROJECT_DIR"
echo "2. Cambiar propietario: sudo chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR"
echo "3. Configurar variables: sudo -u $SERVICE_USER nano $PROJECT_DIR/.env"
echo "4. Reiniciar supervisor: sudo supervisorctl reread && sudo supervisorctl update"
echo "5. Verificar estado: sudo supervisorctl status"
echo ""
echo "🎯 Para configurar rápidamente:"
echo "   sudo ./setup_next_steps.sh"
SCRIPT_END

# 3. CREAR SCRIPT DE SIGUIENTE PASO
echo "📝 Creando script de configuración rápida..."
cat > setup_next_steps.sh << 'NEXT_END'
#!/bin/bash

PROJECT_DIR="/home/ubuntu/neurokup-system"
SERVICE_USER="neurokup"

echo "🚀 CONFIGURACIÓN RÁPIDA DEL PROYECTO"
echo "==================================="

if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "📥 Clonando repositorio..."
    git clone https://github.com/Jos3phil/SysMeReitF1.git $PROJECT_DIR
    sudo chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
fi

echo "⚙️ Creando archivo de configuración..."
sudo -u $SERVICE_USER tee $PROJECT_DIR/.env > /dev/null << EOF
# ================================
# 🔐 CONFIGURACIÓN AWS EC2
# ================================

DEBUG=False
ENVIRONMENT=production
BASE_DIR=$PROJECT_DIR

# COMPLETAR CON TUS CREDENCIALES
KAGGLE_USERNAME=tu_usuario_kaggle
KAGGLE_KEY=tu_api_key_kaggle

COMPETITION_NAME=neuro-kup-ii-beta-acm-ai
MAX_SUBMISSIONS_PER_DAY=7
MIN_IMPROVEMENT_THRESHOLD=0.001

TRAINING_INTERVAL_HOURS=4
VERIFICATION_INTERVAL_MINUTES=30

LOG_LEVEL=INFO
EOF

echo "📋 Configurando credenciales Kaggle..."
sudo -u $SERVICE_USER mkdir -p /home/$SERVICE_USER/.kaggle
sudo -u $SERVICE_USER tee /home/$SERVICE_USER/.kaggle/kaggle.json > /dev/null << EOF
{
  "username": "tu_usuario_kaggle",
  "key": "tu_api_key_kaggle"
}
EOF
sudo -u $SERVICE_USER chmod 600 /home/$SERVICE_USER/.kaggle/kaggle.json

echo "🔄 Reiniciando supervisor..."
sudo supervisorctl reread
sudo supervisorctl update

echo ""
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=========================="
echo "📝 EDITA TUS CREDENCIALES:"
echo "   sudo -u $SERVICE_USER nano $PROJECT_DIR/.env"
echo "   sudo -u $SERVICE_USER nano /home/$SERVICE_USER/.kaggle/kaggle.json"
echo ""
echo "🚀 INICIAR SISTEMA:"
echo "   sudo supervisorctl start neurokup-automation"
echo "   sudo supervisorctl status"
echo ""
echo "📊 VER LOGS:"
echo "   sudo tail -f $PROJECT_DIR/logs/supervisor_output.log"
NEXT_END

# 4. HACER EJECUTABLES
chmod +x aws_setup.sh
chmod +x setup_next_steps.sh

echo ""
echo "✅ SCRIPTS CREADOS CORRECTAMENTE"
echo "================================"
echo ""
echo "🚀 EJECUTA EN ORDEN:"
echo "1. sudo ./aws_setup.sh"
echo "2. sudo ./setup_next_steps.sh" 
echo "3. Editar credenciales y iniciar sistema"
echo ""
echo "📝 Los archivos están listos con terminaciones Unix correctas"
