#!/bin/bash

# ================================
# 🔧 SCRIPT DE CORRECCIÓN RÁPIDA - AWS
# ================================
# Ejecuta este comando en AWS para corregir el archivo

echo "🔧 CORRIGIENDO TERMINACIONES DE LÍNEA..."

# Instalar dos2unix si no está disponible
if ! command -v dos2unix >/dev/null 2>&1; then
    echo "📦 Instalando dos2unix..."
    sudo apt-get update -y
    sudo apt-get install -y dos2unix
fi

# Corregir el archivo aws_setup.sh
if [ -f "aws_setup.sh" ]; then
    echo "🔄 Convirtiendo terminaciones de línea..."
    dos2unix aws_setup.sh
    chmod +x aws_setup.sh
    echo "✅ Archivo corregido y ejecutable"
    echo ""
    echo "🚀 Ahora ejecuta:"
    echo "   sudo ./aws_setup.sh"
else
    echo "❌ Archivo aws_setup.sh no encontrado"
    echo "📥 Descárgalo primero con:"
    echo "   wget https://raw.githubusercontent.com/Jos3phil/SysMeReitF1/master/cloud_deployment/aws_setup.sh"
fi
