# ================================
# 📖 GUÍA COMPLETA DE DESPLIEGUE EN AWS EC2
# ================================

# 🚀 **GUÍA COMPLETA DE DESPLIEGUE - NEUROKUP II EN AWS EC2**

## 📋 **REQUISITOS PREVIOS**

### **1. Cuenta AWS**
- Cuenta AWS activa
- Conocimientos básicos de EC2
- Presupuesto estimado: $20-50/mes (según instancia)

### **2. Archivos necesarios**
- Código fuente del proyecto
- Credenciales de Kaggle (username + API key)
- (Opcional) Credenciales de AWS S3 para backups

---

## 🏗️ **PASO 1: CONFIGURAR INSTANCIA EC2**

### **1.1 Crear instancia**
```bash
# Recomendaciones:
# - Tipo: t3.medium o t3.large (2-4 vCPU, 4-8 GB RAM)
# - OS: Ubuntu 22.04 LTS
# - Almacenamiento: 20-50 GB GP3
# - Security Group: SSH (22), HTTP (80), HTTPS (443)
```

### **1.2 Conectar por SSH**
```bash
# Desde tu máquina local
ssh -i "tu-key.pem" ubuntu@tu-ip-publica

# Una vez conectado, actualizar sistema
sudo apt update && sudo apt upgrade -y
```

---

## ⚙️ **PASO 2: EJECUTAR SCRIPT DE SETUP**

### **2.1 Elegir el script apropiado**

#### 🎯 **Para Ubuntu 24.04 (Noble Numbat) - RECOMENDADO**
```bash
# Script optimizado para Ubuntu 24.04 con Python 3.12
wget https://raw.githubusercontent.com/Jos3phil/SysMeReitF1/master/cloud_deployment/ubuntu24_setup.sh
chmod +x ubuntu24_setup.sh
./ubuntu24_setup.sh
```

#### 🔄 **Para Ubuntu 22.04/20.04 (Legacy)**
```bash
# Script universal que detecta la versión automáticamente
wget https://raw.githubusercontent.com/Jos3phil/SysMeReitF1/master/cloud_deployment/aws_setup.sh
chmod +x aws_setup.sh
./aws_setup.sh
```

### **2.2 Verificar la versión de Ubuntu**
```bash
# Verificar qué versión tienes
lsb_release -a

# Ubuntu 24.04 → usar ubuntu24_setup.sh
# Ubuntu 22.04/20.04 → usar aws_setup.sh
```
chmod +x aws_setup.sh

# Ejecutar setup (toma 5-10 minutos)
sudo ./aws_setup.sh
```

### **2.2 Verificar instalación**
```bash
# Verificar que todo esté instalado
sudo supervisorctl status
systemctl status supervisor
```

---

## 📁 **PASO 3: COPIAR CÓDIGO DEL PROYECTO**

### **3.1 Clonar repositorio**
```bash
# Cambiar al directorio del proyecto
sudo -u neurokup git clone https://github.com/tu-repo/neurokup-system.git /home/ubuntu/neurokup-system

# O copiar archivos manualmente vía SCP
scp -i "tu-key.pem" -r ./neurokup-local ubuntu@tu-ip:/tmp/
sudo -u neurokup cp -r /tmp/neurokup-local/* /home/ubuntu/neurokup-system/
```

### **3.2 Instalar dependencias Python específicas**
```bash
sudo -u neurokup /home/ubuntu/neurokup-system/venv/bin/pip install -r requirements.txt
```

---

## 🔐 **PASO 4: CONFIGURAR CREDENCIALES**

### **4.1 Crear archivo de variables de entorno**
```bash
sudo -u neurokup nano /home/ubuntu/neurokup-system/.env
```

### **4.2 Completar configuración**
```env
# Variables básicas
DEBUG=False
ENVIRONMENT=production
BASE_DIR=/home/ubuntu/neurokup-system

# Credenciales de Kaggle
KAGGLE_USERNAME=tu_usuario_kaggle
KAGGLE_KEY=tu_api_key_de_kaggle

# Configuración de competencia
COMPETITION_NAME=neuro-kup-ii-beta-acm-ai
MAX_SUBMISSIONS_PER_DAY=7
MIN_IMPROVEMENT_THRESHOLD=0.001

# Intervalos de tiempo
TRAINING_INTERVAL_HOURS=4
VERIFICATION_INTERVAL_MINUTES=30

# Configuración de logs
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Monitoreo
HEALTH_CHECK_INTERVAL=300
MAX_MEMORY_MB=2048
MAX_CPU_PERCENT=80

# Email (opcional)
EMAIL_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
ADMIN_EMAIL=admin@example.com

# Slack (opcional)
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# AWS S3 para backups (opcional)
S3_BACKUP_ENABLED=false
S3_BACKUP_BUCKET=tu-bucket-de-backups
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
```

### **4.3 Configurar credenciales de Kaggle**
```bash
# Crear directorio .kaggle
sudo -u neurokup mkdir -p /home/ubuntu/.kaggle

# Crear archivo de credenciales
sudo -u neurokup tee /home/ubuntu/.kaggle/kaggle.json << EOF
{
  "username": "tu_usuario_kaggle",
  "key": "tu_api_key"
}
EOF

# Configurar permisos
sudo -u neurokup chmod 600 /home/ubuntu/.kaggle/kaggle.json
```

---

## 🚀 **PASO 5: INICIAR EL SISTEMA**

### **5.1 Configurar supervisor**
```bash
# Verificar configuración
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar el servicio
sudo supervisorctl start neurokup-automation

# Verificar estado
sudo supervisorctl status
```

### **5.2 Verificar logs**
```bash
# Ver logs en tiempo real
sudo tail -f /home/ubuntu/neurokup-system/logs/supervisor_output.log

# Ver logs de errores
sudo tail -f /home/ubuntu/neurokup-system/logs/supervisor_error.log

# Ver logs del sistema
sudo tail -f /home/ubuntu/neurokup-system/logs/neurokup.log
```

---

## 📊 **PASO 6: MONITOREO Y MANTENIMIENTO**

### **6.1 Comandos útiles de supervisor**
```bash
# Ver estado de todos los servicios
sudo supervisorctl status

# Reiniciar el servicio
sudo supervisorctl restart neurokup-automation

# Detener el servicio
sudo supervisorctl stop neurokup-automation

# Ver logs en vivo
sudo supervisorctl tail -f neurokup-automation
```

### **6.2 Monitoreo del sistema**
```bash
# Ver recursos del sistema
htop

# Ver espacio en disco
df -h

# Ver logs de sistema
journalctl -u supervisor -f

# Ver procesos Python
ps aux | grep python
```

### **6.3 Verificar funcionamiento**
```bash
# Verificar que el sistema está entrenando
sudo -u neurokup ls -la /home/ubuntu/neurokup-system/models/

# Verificar submissions
sudo -u neurokup ls -la /home/ubuntu/neurokup-system/submissions/

# Verificar base de datos
sudo -u neurokup sqlite3 /home/ubuntu/neurokup-system/data/submissions.db ".tables"
```

---

## 🔧 **CONFIGURACIONES AVANZADAS**

### **7.1 Configurar firewall UFW**
```bash
# Configurar firewall básico
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from tu-ip-local to any port 22  # Solo tu IP para SSH
sudo ufw status
```

### **7.2 Configurar backup automático a S3**
```bash
# Instalar AWS CLI
sudo apt install awscli -y

# Configurar credenciales
sudo -u neurokup aws configure
```

### **7.3 Configurar auto-scaling (opcional)**
```bash
# Crear script de monitoreo de recursos
sudo nano /home/ubuntu/check_resources.sh

#!/bin/bash
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f"), $3/$2 * 100.0}')
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')

if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
    echo "High memory usage: $MEMORY_USAGE%"
    # Aquí puedes agregar lógica para escalar o alertar
fi
```

### **7.4 Configurar SSL/HTTPS (si planeas exponer APIs)**
```bash
# Instalar Certbot
sudo apt install certbot -y

# Obtener certificado (necesitas dominio)
sudo certbot certonly --standalone -d tu-dominio.com
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **8.1 El servicio no inicia**
```bash
# Verificar logs de supervisor
sudo tail -f /var/log/supervisor/supervisord.log

# Verificar configuración
sudo supervisorctl reread

# Verificar permisos
sudo chown -R neurokup:neurokup /home/ubuntu/neurokup-system/
```

### **8.2 Errores de credenciales de Kaggle**
```bash
# Verificar archivo de credenciales
sudo -u neurokup cat /home/ubuntu/.kaggle/kaggle.json

# Probar manualmente
sudo -u neurokup /home/ubuntu/neurokup-system/venv/bin/python -c "import kaggle; kaggle.api.authenticate()"
```

### **8.3 Problemas de memoria**
```bash
# Verificar uso de memoria
free -h

# Configurar swap si es necesario
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### **8.4 Problemas de conectividad**
```bash
# Verificar conectividad a Kaggle
curl -I https://www.kaggle.com

# Verificar DNS
nslookup kaggle.com

# Verificar reglas de firewall
sudo ufw status verbose
```

---

## 💰 **ESTIMACIÓN DE COSTOS**

### **9.1 Costos típicos en AWS**
```
t3.medium (2 vCPU, 4GB RAM):
- Bajo demanda: ~$30/mes
- Spot instance: ~$9/mes
- Reserved (1 año): ~$20/mes

t3.large (2 vCPU, 8GB RAM):
- Bajo demanda: ~$60/mes
- Spot instance: ~$18/mes
- Reserved (1 año): ~$35/mes

Almacenamiento (20GB GP3): ~$2/mes
Transferencia de datos: ~$1-5/mes
```

### **9.2 Optimización de costos**
- Usar **Spot Instances** (70% más barato)
- Configurar **Auto Stop** cuando no hay competencias
- Usar **S3 IA** para backups
- Monitorear uso con **AWS Cost Explorer**

---

## ✅ **CHECKLIST DE DESPLIEGUE**

### **Pre-despliegue**
- [ ] Cuenta AWS configurada
- [ ] Credenciales de Kaggle válidas
- [ ] Código fuente actualizado
- [ ] Variables de entorno definidas

### **Durante el despliegue**
- [ ] Instancia EC2 creada y corriendo
- [ ] Script de setup ejecutado sin errores
- [ ] Código copiado al servidor
- [ ] Variables de entorno configuradas
- [ ] Credenciales de Kaggle configuradas
- [ ] Supervisor iniciado y funcionando

### **Post-despliegue**
- [ ] Logs del sistema sin errores
- [ ] Primer entrenamiento completado
- [ ] Base de datos creada
- [ ] Backups funcionando
- [ ] Monitoreo activo
- [ ] Notificaciones configuradas (opcional)

### **Verificación final**
- [ ] Sistema ejecutándose por al menos 24 horas
- [ ] Al menos una submission automática realizada
- [ ] Logs de todas las funcionalidades sin errores
- [ ] Recursos del servidor dentro de límites normales

---

## 🎯 **MEJORES PRÁCTICAS**

### **10.1 Seguridad**
- Cambiar puerto SSH por defecto
- Usar solo autenticación por clave
- Configurar fail2ban para SSH
- Actualizar sistema regularmente
- Rotar credenciales periódicamente

### **10.2 Monitoreo**
- Configurar alertas de memoria/CPU
- Monitorear logs regularmente
- Configurar backups automáticos
- Verificar submissions periódicamente

### **10.3 Mantenimiento**
- Actualizar dependencias mensualmente
- Limpiar logs antiguos
- Verificar espacio en disco
- Revisar y optimizar modelos

### **10.4 Escalabilidad**
- Usar Load Balancer para múltiples instancias
- Configurar Auto Scaling Groups
- Usar RDS para base de datos en producción
- Implementar CI/CD para actualizaciones

---

## 📞 **SOPORTE Y RECURSOS**

### **11.1 Logs importantes**
```bash
# Sistema principal
/home/ubuntu/neurokup-system/logs/neurokup.log

# Supervisor
/home/ubuntu/neurokup-system/logs/supervisor_output.log
/home/ubuntu/neurokup-system/logs/supervisor_error.log

# Sistema operativo
/var/log/syslog
/var/log/supervisor/supervisord.log
```

### **11.2 Comandos de diagnóstico**
```bash
# Estado general del sistema
sudo systemctl status supervisor
sudo supervisorctl status
ps aux | grep python
df -h
free -h
top

# Conectividad
ping kaggle.com
curl -I https://www.kaggle.com
nc -zv kaggle.com 443

# Logs en tiempo real
sudo tail -f /home/ubuntu/neurokup-system/logs/neurokup.log
```

---

## 🎉 **¡SISTEMA LISTO!**

Una vez completados todos los pasos, tendrás:

✅ **Sistema 24/7** ejecutándose automáticamente  
✅ **Entrenamientos automáticos** cada 4 horas  
✅ **Submissions inteligentes** solo cuando hay mejoras  
✅ **Monitoreo robusto** con alertas  
✅ **Backups automáticos** para proteger el trabajo  
✅ **Logging completo** para debugging  
✅ **Configuración de producción** optimizada  

El sistema ahora funcionará automáticamente, entrenando modelos, mejorándolos iterativamente y realizando submissions cuando detecte mejoras significativas en el F1-Score.

**¡Tu sistema de ML automático está listo para competir! 🚀**
