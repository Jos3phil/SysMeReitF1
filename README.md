# 🚀 SysMeReitF1 - Sistema de Mejora Reiterativa para F1-Score

Sistema automático de machine learning para la competencia **NeuroKup II** con entrenamiento continuo, mejora iterativa y submissions automáticas.

## 🎯 **Características Principales**

### 🤖 **Automatización Completa**
- ✅ Entrenamiento automático cada 4 horas
- ✅ Mejora iterativa con 10+ estrategias avanzadas
- ✅ Submissions inteligentes solo cuando hay mejora
- ✅ Monitoreo 24/7 con alertas
- ✅ Backups automáticos

### 🧠 **Machine Learning Avanzado**
- ✅ Ensemble de múltiples modelos (RF, XGBoost, LightGBM)
- ✅ Feature engineering automático
- ✅ Hyperparameter optimization
- ✅ Cross-validation robusta
- ✅ Threshold optimization

### ☁️ **Despliegue en la Nube**
- ✅ Configurado para AWS EC2
- ✅ Supervisor para gestión de servicios
- ✅ Monitoreo de recursos del sistema
- ✅ Backups automáticos a S3
- ✅ Notificaciones por email/Slack

## 📁 **Estructura del Proyecto**

```
SysMeReitF1/
├── automatizacion/                 # 🤖 Sistema de ML automático
│   ├── calcularf1_score.py        # Motor principal de ML
│   ├── mejora_iterativa.py        # Optimización iterativa
│   ├── api_submission_automatica.py # Submissions automáticas
│   └── setup_completo.py          # Instalador automático
├── cloud_deployment/              # ☁️ Despliegue en la nube
│   ├── aws_setup.sh               # Script de instalación AWS
│   ├── production_config.py       # Configuración de producción
│   ├── main.py                    # Sistema principal
│   ├── monitoring_system.py       # Monitoreo y alertas
│   ├── backup_manager.py          # Gestión de backups
│   ├── requirements.txt           # Dependencias
│   └── DEPLOYMENT_GUIDE.md        # Guía de despliegue
├── main_production.py             # 🚀 Punto de entrada principal
└── README.md                      # Esta documentación
```

## ⚡ **Inicio Rápido**

### **Opción 1: Instalación Local (Windows/Linux)**

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Jos3phil/SysMeReitF1.git
cd SysMeReitF1
```

2. **Ejecutar setup automático:**
```bash
python automatizacion/setup_completo.py
```

3. **Configurar credenciales de Kaggle:**
```bash
python inicio_rapido.py
# Opción 1: Configurar credenciales
```

4. **Iniciar sistema automático:**
```bash
python inicio_rapido.py
# Opción 3: Sistema automático completo
```

### **Opción 2: Despliegue en AWS EC2**

1. **Crear instancia EC2** (Ubuntu 22.04, t3.medium o superior)

2. **Ejecutar script de setup:**
```bash
wget https://raw.githubusercontent.com/Jos3phil/SysMeReitF1/main/cloud_deployment/aws_setup.sh
chmod +x aws_setup.sh
sudo ./aws_setup.sh
```

3. **Seguir la guía completa:** [`DEPLOYMENT_GUIDE.md`](cloud_deployment/DEPLOYMENT_GUIDE.md)

## 🎮 **Uso del Sistema**

### **Funciones Principales:**

```python
# 1. Obtener F1-Score de un dataset
import automatizacion.calcularf1_score as cf1
predicciones, f1_score = cf1.obtener_score('test_public.csv')

# 2. Mejorar modelo automáticamente
from automatizacion.mejora_iterativa import mejorar_modelo_automatico
mejor_modelo, score, historial = mejorar_modelo_automatico('train.csv')

# 3. Sistema automático completo
from automatizacion.api_submission_automatica import iniciar_sistema_automatico
iniciar_sistema_automatico()  # Corre 24/7
```

### **Comandos de Supervisión:**

```bash
# Ver estado del sistema
sudo supervisorctl status

# Ver logs en tiempo real
sudo tail -f /home/ubuntu/neurokup-system/logs/neurokup.log

# Reiniciar sistema
sudo supervisorctl restart neurokup-automation
```

## 📊 **Estrategias de Mejora**

El sistema implementa automáticamente:

1. **Hyperparameter Optimization** - RandomizedSearchCV con múltiples modelos
2. **Feature Engineering** - Interacciones, selección, transformaciones
3. **Ensemble Methods** - Voting, Stacking, Bagging
4. **Data Balancing** - SMOTE, ADASYN, undersampling
5. **Threshold Optimization** - Búsqueda del punto óptimo
6. **Cross-Validation** - Validación robusta anti-overfitting

## 🏆 **Resultados Esperados**

Con un F1-Score base de 0.9579, el sistema puede lograr mejoras de:
- **+0.005-0.015** con optimización de hiperparámetros
- **+0.003-0.010** con feature engineering avanzado
- **+0.002-0.008** con ensemble sofisticado
- **Objetivo: 0.97-0.98** (Top 5% competencias)

## 🔧 **Configuración**

### **Variables de Entorno Principales:**
```env
# Credenciales Kaggle
KAGGLE_USERNAME=tu_usuario
KAGGLE_KEY=tu_api_key

# Configuración del sistema
TRAINING_INTERVAL_HOURS=4
MAX_SUBMISSIONS_PER_DAY=7
MIN_IMPROVEMENT_THRESHOLD=0.001

# Monitoreo
LOG_LEVEL=INFO
MAX_MEMORY_MB=2048
MAX_CPU_PERCENT=80
```

### **Archivos Requeridos:**
- `train.csv` o `train_local.csv` - Dataset de entrenamiento
- `test_public.csv` - Test con target (para validación)
- `test_private.csv` - Test sin target (para submission final)

## 💰 **Costos AWS Estimados**

| Instancia | Costo/mes | Descripción |
|-----------|-----------|-------------|
| t3.medium | $30 | 2 vCPU, 4GB RAM |
| t3.large | $60 | 2 vCPU, 8GB RAM (recomendado) |
| Spot instances | -70% | Ahorro significativo |

## 🚨 **Troubleshooting**

### **Problemas Comunes:**

1. **Error de credenciales Kaggle:**
```bash
# Verificar archivo
cat ~/.kaggle/kaggle.json
# Regenerar en: https://www.kaggle.com/account
```

2. **Sistema no inicia:**
```bash
# Ver logs
sudo tail -f /var/log/supervisor/supervisord.log
sudo supervisorctl reread && sudo supervisorctl update
```

3. **Memoria insuficiente:**
```bash
# Verificar uso
free -h
# Configurar swap si es necesario
```

## 📈 **Monitoreo y Métricas**

El sistema incluye:
- **Dashboard de métricas** en tiempo real
- **Alertas automáticas** por email/Slack
- **Historial completo** de entrenamientos y submissions
- **Health checks** cada 5 minutos
- **Backups automáticos** diarios

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 **Soporte**

- **Issues:** [GitHub Issues](https://github.com/Jos3phil/SysMeReitF1/issues)
- **Documentación:** [Guía de Despliegue](cloud_deployment/DEPLOYMENT_GUIDE.md)
- **Email:** [tu-email@ejemplo.com]

---

## 🎯 **Próximos Pasos**

1. **Configurar el sistema** siguiendo el inicio rápido
2. **Subir tus datasets** al directorio del proyecto
3. **Configurar credenciales** de Kaggle
4. **Iniciar el sistema automático**
5. **Monitorear los primeros ciclos** de entrenamiento
6. **Desplegar en AWS** para operación 24/7

**¡Buena suerte en la competencia! 🚀**

---

*Sistema desarrollado para NeuroKup II - Automatización inteligente de machine learning competitivo*
