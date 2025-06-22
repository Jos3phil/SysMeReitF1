# 🚀 GUÍA RÁPIDA: SCRIPTS DE INSTALACIÓN

## 📋 Resumen de Scripts Disponibles

| Script | Uso Recomendado | Python | Descripción |
|--------|-----------------|--------|-------------|
| `ubuntu24_setup.sh` | **Ubuntu 24.04** (AWS EC2 nuevo) | 3.12 | Script optimizado para Ubuntu 24.04 Noble |
| `aws_setup.sh` | **Ubuntu 22.04/20.04** (AWS EC2 legacy) | 3.9/3.12 | Script universal con detección automática |
| `setup_linux.sh` | **Linux Mint** (desarrollo local) | 3.x | Setup para entorno de desarrollo local |

---

## 🎯 INSTRUCCIONES RÁPIDAS POR ESCENARIO

### 🔥 **AWS EC2 - Ubuntu 24.04 (RECOMENDADO)**
```bash
# 1. Conectar a la instancia
ssh -i "tu-key.pem" ubuntu@tu-ip-ec2

# 2. Verificar versión (debe ser 24.04)
lsb_release -a

# 3. Ejecutar script optimizado
wget https://raw.githubusercontent.com/Jos3phil/SysMeReitF1/master/cloud_deployment/ubuntu24_setup.sh
chmod +x ubuntu24_setup.sh
./ubuntu24_setup.sh
```

### 🔄 **AWS EC2 - Ubuntu 22.04/20.04 (Legacy)**
```bash
# 1. Conectar a la instancia
ssh -i "tu-key.pem" ubuntu@tu-ip-ec2

# 2. Ejecutar script universal
wget https://raw.githubusercontent.com/Jos3phil/SysMeReitF1/master/cloud_deployment/aws_setup.sh
chmod +x aws_setup.sh
./aws_setup.sh
```

### 🏠 **Linux Mint (Desarrollo Local)**
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/neurokup-ii-system.git
cd neurokup-ii-system

# 2. Ejecutar setup
chmod +x setup_linux.sh
./setup_linux.sh
```

---

## ⚡ RESOLUCIÓN DE PROBLEMAS COMUNES

### 🐍 **Error: "python3.9 no encontrado" en Ubuntu 24.04**
**Solución:** Usar `ubuntu24_setup.sh` en lugar de `aws_setup.sh`

### 📦 **Error: "No module named 'xxx'" después de la instalación**
```bash
# Activar entorno virtual y reinstalar
source /home/ubuntu/neurokup-system/venv/bin/activate
pip install --upgrade pip
pip install pandas numpy scikit-learn
```

### 🔒 **Error: "Permission denied" al ejecutar script**
```bash
# Asegurar permisos correctos
chmod +x *.sh
```

### 🌐 **Error: "Connection refused" en puerto 8000**
```bash
# Verificar firewall y servicios
sudo ufw status
sudo systemctl status nginx
sudo supervisorctl status
```

---

## 🔍 VERIFICACIÓN POST-INSTALACIÓN

### Comandos de verificación:
```bash
# Estado general del sistema
/home/ubuntu/neurokup-system/check_status.sh

# Logs en tiempo real
sudo tail -f /var/log/neurokup-*.log

# Estado de servicios
sudo supervisorctl status
sudo systemctl status nginx

# Prueba de conectividad
curl http://localhost:8000/health
curl http://$(curl -s ifconfig.me)/health
```

---

## 📞 SOPORTE

Si tienes problemas:
1. **Verificar logs:** `sudo tail -f /var/log/neurokup-error.log`
2. **Revisar versión de Ubuntu:** `lsb_release -a`
3. **Probar script específico** según tu versión de Ubuntu
4. **Revisar documentación completa:** `DEPLOYMENT_GUIDE.md`

---

## 🎉 ¡ÉXITO!

Cuando veas:
```
🎉 ¡Sistema listo para usar!
```

Tu sistema está completamente configurado y ejecutándose. Accede a `http://tu-ip-ec2` para verificar que funciona.
