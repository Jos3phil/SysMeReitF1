# ================================
# 🐧 COMANDOS RÁPIDOS PARA LINUX MINT
# ================================

# 🚀 COMANDOS MÁS USADOS PARA DESARROLLO

## 📥 Clonar e instalar (primera vez)
```bash
git clone https://github.com/Jos3phil/SysMeReitF1.git
cd SysMeReitF1
chmod +x setup_linux.sh
./setup_linux.sh
```

## ⚙️ Configuración rápida
```bash
# Editar credenciales de Kaggle
nano .env

# Configurar credenciales de Kaggle (alternativo)
mkdir -p ~/.kaggle
echo '{"username":"tu_usuario","key":"tu_api_key"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

## 🔄 Activar entorno y trabajar
```bash
# Activar entorno virtual
source venv/bin/activate

# Verificar instalación
python -c "import pandas, sklearn, xgboost; print('✅ Todo instalado')"

# Probar sistema básico
python ejemplo_uso_calcularf1.py
```

## 🧪 Comandos de desarrollo
```bash
# Ejecutar una mejora manual
python -c "
from automatizacion.mejora_iterativa import mejorar_modelo_automatico
resultado = mejorar_modelo_automatico('data/train.csv')
print(f'Mejor score: {resultado[1]:.4f}')
"

# Generar predicciones rápidas
python -c "
import automatizacion.calcularf1_score as cf1
pred, f1 = cf1.obtener_score('data/test_public.csv')
print(f'F1-Score: {f1:.4f}')
"

# Verificar datasets
ls -la data/
file data/*.csv
```

## 🚀 Ejecutar sistema completo
```bash
# Sistema automático (Ctrl+C para parar)
python main_production.py

# En segundo plano
nohup python main_production.py > logs/sistema.log 2>&1 &

# Ver logs en tiempo real
tail -f logs/neurokup.log
```

## 📊 Monitoreo y depuración
```bash
# Ver recursos del sistema
htop
free -h
df -h

# Ver procesos Python
ps aux | grep python

# Verificar logs
tail -n 50 logs/neurokup.log
grep "ERROR" logs/neurokup.log

# Limpiar logs
> logs/neurokup.log
```

## 🔄 Git workflow rápido
```bash
# Actualizar desde GitHub
git pull origin master

# Subir cambios
git add .
git commit -m "🐧 Mejoras desde Linux Mint"
git push origin master

# Ver estado
git status
git log --oneline -10
```

## 🧹 Mantenimiento
```bash
# Limpiar archivos temporales
rm -rf __pycache__/
rm -rf .pytest_cache/
find . -name "*.pyc" -delete

# Actualizar dependencias
pip install --upgrade -r cloud_deployment/requirements.txt

# Backup rápido
tar -czf backup_$(date +%Y%m%d).tar.gz \
    automatizacion/ cloud_deployment/ *.py .env

# Limpiar modelos antiguos
find models/ -name "*.pkl" -mtime +7 -delete
```

## 🚨 Troubleshooting rápido
```bash
# Error de memoria
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo swapon --show

# Error de permisos
chmod +x automatizacion/*.py
chmod +x *.py

# Reinstalar dependencias
pip install --force-reinstall -r cloud_deployment/requirements.txt

# Verificar Kaggle
python -c "import kaggle; kaggle.api.authenticate(); print('✅ Kaggle OK')"
```

## ⚡ Desarrollo súper rápido
```bash
# Alias útiles (agregar a ~/.bashrc)
alias activate="source venv/bin/activate"
alias neurokup="cd ~/SysMeReitF1 && source venv/bin/activate"
alias train="python -c 'from automatizacion.mejora_iterativa import *'"
alias predict="python automatizacion/calcularf1_score.py"
alias logs="tail -f logs/neurokup.log"

# Recarga alias
source ~/.bashrc
```

## 🎯 Workflow típico de desarrollo
```bash
# 1. Activar entorno
neurokup  # (si tienes el alias)

# 2. Actualizar código
git pull

# 3. Probar cambios
python ejemplo_uso_calcularf1.py

# 4. Entrenar modelo
python -c "
from automatizacion.mejora_iterativa import mejorar_modelo_automatico
resultado = mejorar_modelo_automatico('data/train.csv')
print(f'✅ Nuevo score: {resultado[1]:.4f}')
"

# 5. Generar submission
python -c "
import automatizacion.calcularf1_score as cf1
cf1.procesar_ambos_datasets()
print('✅ Submission generada')
"

# 6. Subir cambios
git add . && git commit -m "🚀 Mejora $(date)" && git push
```

## 🔥 Tips para Linux Mint
```bash
# Usar todos los cores del CPU
export OMP_NUM_THREADS=$(nproc)
export MKL_NUM_THREADS=$(nproc)

# Optimizar Python para ML
export PYTHONHASHSEED=0
export CUDA_VISIBLE_DEVICES=0  # Si tienes GPU

# Monitoreo de recursos en terminal
watch -n 1 'free -h && echo && df -h | head -2'

# Abrir múltiples terminales para monitoreo
gnome-terminal --tab --title="Logs" -- bash -c "cd ~/SysMeReitF1 && tail -f logs/neurokup.log"
gnome-terminal --tab --title="Htop" -- htop
```

---

**💡 TIP PRINCIPAL:** Linux Mint es mucho más rápido para ML que Windows. 
¡Aprovecha esa velocidad para iterar más rápido y encontrar mejores modelos! 🚀
