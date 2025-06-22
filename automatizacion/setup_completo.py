# ================================
# 🚀 SETUP COMPLETO - SISTEMA AUTOMÁTICO NEUROKUP II
# ================================
# Instalación y configuración completa en un solo archivo

import os
import sys
import subprocess
import json
from pathlib import Path

def instalar_dependencias():
    """Instalar todas las dependencias necesarias"""
    
    print("📦 INSTALANDO DEPENDENCIAS")
    print("="*40)
    
    dependencias = [
        'pandas',
        'numpy', 
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'requests',
        'schedule',
        'imbalanced-learn',  # Para SMOTE
        'xgboost',           # Para XGBoost
        'lightgbm',          # Para LightGBM
        'kaggle'             # Para API de Kaggle
    ]
    
    for dep in dependencias:
        try:
            print(f"📥 Instalando {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"⚠️ Error instalando {dep} - se puede instalar manualmente")
    
    print("✅ Instalación de dependencias completada")

def crear_estructura_directorios():
    """Crear estructura de directorios necesaria"""
    
    print("\n📁 CREANDO ESTRUCTURA DE DIRECTORIOS")
    print("="*40)
    
    directorios = [
        'models_backup',
        'submissions_backup', 
        'logs',
        'data',
        'config'
    ]
    
    for directorio in directorios:
        Path(directorio).mkdir(exist_ok=True)
        print(f"📂 {directorio}/")
    
    print("✅ Estructura de directorios creada")

def crear_archivo_configuracion():
    """Crear archivo de configuración base"""
    
    print("\n⚙️ CREANDO CONFIGURACIÓN BASE")
    print("="*40)
    
    config = {
        "competencia": {
            "nombre": "neuro-kup-ii-beta-acm-ai",
            "url": "https://www.kaggle.com/competitions/neuro-kup-ii-beta-acm-ai",
            "max_submissions_per_day": 7,
            "min_mejora_requerida": 0.001
        },
        "entrenamiento": {
            "intervalo_horas": 4,
            "estrategias": [
                "hyperparameter_optimization",
                "feature_engineering",
                "ensemble_avanzado", 
                "balanceado_datos"
            ],
            "cv_folds": 5,
            "scoring": "f1"
        },
        "submission": {
            "verificacion_intervalo_minutos": 30,
            "auto_submit": True,
            "backup_submissions": True
        },
        "logging": {
            "level": "INFO",
            "archivo": "logs/sistema.log",
            "formato": "%(asctime)s - %(levelname)s - %(message)s"
        }
    }
    
    with open('config/sistema_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Archivo de configuración creado: config/sistema_config.json")

def crear_script_inicio():
    """Crear script de inicio rápido"""
    
    print("\n🚀 CREANDO SCRIPT DE INICIO")
    print("="*40)
    
    script_inicio = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 INICIO RÁPIDO - SISTEMA AUTOMÁTICO NEUROKUP II
Ejecuta este archivo para iniciar todo el sistema
"""

import sys
import os
from pathlib import Path

# Añadir directorio actual al path
sys.path.append(str(Path(__file__).parent))

try:
    from api_submission_automatica import iniciar_sistema_automatico, configurar_credenciales
    from mejora_iterativa import mejorar_modelo_automatico
    import calcularf1_score
    
    print("🚀 SISTEMA AUTOMÁTICO NEUROKUP II")
    print("="*50)
    print("✅ Todos los módulos cargados correctamente")
    
    # Verificar archivos necesarios
    archivos_necesarios = [
        'train_local.csv',
        'test_public.csv', 
        'test_private.csv'
    ]
    
    archivos_faltantes = [f for f in archivos_necesarios if not os.path.exists(f)]
    
    if archivos_faltantes:
        print(f"⚠️ Archivos faltantes: {archivos_faltantes}")
        print("📋 Asegúrate de tener los datasets en el directorio principal")
        
        continuar = input("¿Continuar de todas formas? (s/n): ").lower().strip()
        if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
            sys.exit("❌ Proceso cancelado")
    
    print("\\n📋 OPCIONES DISPONIBLES:")
    print("1️⃣ Configurar credenciales de Kaggle")
    print("2️⃣ Probar mejora de modelo (una vez)")
    print("3️⃣ Iniciar sistema automático completo")
    print("4️⃣ Enviar submission manual")
    print("5️⃣ Ver estadísticas")
    print("0️⃣ Salir")
    
    while True:
        opcion = input("\\nSelecciona una opción (0-5): ").strip()
        
        if opcion == "1":
            username = input("Username de Kaggle: ")
            api_key = input("API Key de Kaggle: ")
            configurar_credenciales(username, api_key)
            print("✅ Credenciales configuradas")
        
        elif opcion == "2":
            print("🤖 Iniciando mejora de modelo...")
            try:
                mejor_modelo, mejor_score, historial = mejorar_modelo_automatico('train_local.csv')
                print(f"🏆 Mejor score obtenido: {mejor_score:.4f}")
                print(f"📋 Mejoras encontradas: {len([h for h in historial if h['mejora']])}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif opcion == "3":
            print("🚀 Iniciando sistema automático...")
            try:
                iniciar_sistema_automatico()
            except KeyboardInterrupt:
                print("\\n🛑 Sistema detenido por usuario")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif opcion == "4":
            archivo = input("Archivo CSV de submission: ")
            mensaje = input("Mensaje (opcional): ") or "Submission manual"
            try:
                from api_submission_automatica import enviar_submission_manual
                enviar_submission_manual(archivo, mensaje)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif opcion == "5":
            try:
                from api_submission_automatica import DatabaseManager
                db = DatabaseManager()
                stats = db.obtener_estadisticas()
                
                print("\\n📊 ESTADÍSTICAS:")
                print(f"  Total submissions: {stats['total_submissions']}")
                print(f"  Submissions hoy: {stats['submissions_hoy']}")
                print(f"  Mejor score: {stats['mejor_score_publico']}")
                
            except Exception as e:
                print(f"❌ Error obteniendo estadísticas: {e}")
        
        elif opcion == "0":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")

except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de tener todos los archivos en el directorio:")
    print("  - calcularf1_score.py")
    print("  - mejora_iterativa.py") 
    print("  - api_submission_automatica.py")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
'''
    
    with open('inicio_rapido.py', 'w', encoding='utf-8') as f:
        f.write(script_inicio)
    
    print("✅ Script de inicio creado: inicio_rapido.py")

def crear_archivo_requirements():
    """Crear archivo requirements.txt"""
    
    print("\n📋 CREANDO REQUIREMENTS.TXT")
    print("="*40)
    
    requirements = """# Dependencias para Sistema Automático NeuroKup II
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
seaborn>=0.11.0
requests>=2.25.0
schedule>=1.1.0
imbalanced-learn>=0.8.0
xgboost>=1.5.0
lightgbm>=3.3.0
kaggle>=1.5.0

# Opcional para mejores visualizaciones
plotly>=5.0.0
jupyter>=1.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Requirements.txt creado")

def crear_readme():
    """Crear archivo README con instrucciones"""
    
    print("\n📖 CREANDO README")
    print("="*40)
    
    readme = """# 🤖 Sistema Automático NeuroKup II

Sistema completo de entrenamiento automático y submissions para la competencia NeuroKup II.

## 🚀 Inicio Rápido

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Colocar datasets:**
   - `train_local.csv` o `train_colab.csv`
   - `test_public.csv`
   - `test_private.csv`

3. **Ejecutar:**
   ```bash
   python inicio_rapido.py
   ```

## 📋 Características

### 🤖 Entrenamiento Automático
- ✅ Optimización de hiperparámetros
- ✅ Feature engineering avanzado  
- ✅ Ensemble de múltiples modelos
- ✅ Balanceado inteligente de datos
- ✅ Validación cruzada robusta

### 📤 Submissions Automáticas
- ✅ 7 submissions diarias automáticas
- ✅ Solo sube si hay mejora
- ✅ Monitoreo continuo de resultados
- ✅ Base de datos de historial
- ✅ Backup automático de modelos

### 📊 Monitoreo
- ✅ Logging completo de actividad
- ✅ Estadísticas en tiempo real
- ✅ Reporte de mejoras
- ✅ Dashboard de resultados

## 🔧 Configuración

### Credenciales de Kaggle
1. Ve a: https://www.kaggle.com/account
2. Crea nueva API token
3. Configura con: `configurar_credenciales(username, api_key)`

### Configuración Avanzada
Edita `config/sistema_config.json` para personalizar:
- Intervalos de entrenamiento
- Estrategias de mejora
- Límites de submissions
- Logging

## 📁 Estructura

```
proyecto/
├── calcularf1_score.py          # Módulo ML base
├── mejora_iterativa.py          # Optimización automática  
├── api_submission_automatica.py # Sistema de submissions
├── inicio_rapido.py             # Script principal
├── requirements.txt             # Dependencias
├── config/
│   └── sistema_config.json      # Configuración
├── models_backup/               # Modelos guardados
├── submissions_backup/          # Submissions backup
└── logs/                        # Logs del sistema
```

## 🎯 Uso Avanzado

### Mejora Manual
```python
from mejora_iterativa import mejorar_modelo_automatico

modelo, score, historial = mejorar_modelo_automatico('train.csv')
print(f"Mejor score: {score:.4f}")
```

### Submission Manual
```python
from api_submission_automatica import enviar_submission_manual

enviar_submission_manual('mi_submission.csv', 'Mi mensaje')
```

### Sistema Automático
```python
from api_submission_automatica import iniciar_sistema_automatico

iniciar_sistema_automatico()  # Corre 24/7
```

## 📊 Métricas

El sistema optimiza para **F1-Score** considerando:
- Dataset desbalanceado (8% positivos)
- Validación cruzada estratificada
- Threshold optimization
- Ensemble de modelos diversos

## 🛡️ Seguridad

- ✅ Credenciales encriptadas localmente
- ✅ Backups automáticos de modelos
- ✅ Logging de todas las actividades
- ✅ Límites de rate para API

## 🔍 Troubleshooting

### Error de importación
```bash
pip install -r requirements.txt
```

### Error de credenciales
1. Regenera API key en Kaggle
2. Ejecuta: `configurar_credenciales(nuevo_username, nuevo_key)`

### Sin mejoras
- Verifica calidad de datos
- Ajusta `min_mejora_requerida` en config
- Prueba diferentes estrategias

## 📈 Roadmap

- [ ] Integración con Weights & Biases
- [ ] Alertas por Slack/Discord
- [ ] Dashboard web en tiempo real
- [ ] Auto-scaling en cloud
- [ ] Ensemble cross-validation

## 🤝 Contribuir

1. Fork el proyecto
2. Crea feature branch
3. Commit cambios
4. Push al branch  
5. Abre Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE

---

🏆 **¡Buena suerte en la competencia!** 🏆
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("✅ README.md creado")

def crear_ejemplo_uso():
    """Crear archivo de ejemplo de uso"""
    
    print("\n💡 CREANDO EJEMPLO DE USO")
    print("="*40)
    
    ejemplo = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💡 EJEMPLO DE USO - Sistema Automático NeuroKup II
Este archivo muestra cómo usar cada funcionalidad
"""

import pandas as pd
from datetime import datetime

# ================================
# 1️⃣ MEJORA MANUAL DE MODELO
# ================================

def ejemplo_mejora_manual():
    """Ejemplo de mejora manual del modelo"""
    
    print("🤖 EJEMPLO: Mejora manual de modelo")
    print("="*40)
    
    from mejora_iterativa import mejorar_modelo_automatico
    
    # Entrenar con mejoras automáticas
    mejor_modelo, mejor_score, historial = mejorar_modelo_automatico(
        archivo_train='train_local.csv',
        score_base=0.98  # Score base a superar
    )
    
    print(f"🏆 Mejor score: {mejor_score:.4f}")
    print(f"📋 Mejoras probadas: {len(historial)}")
    
    # Ver mejoras significativas
    mejoras = [h for h in historial if h['mejora']]
    print(f"✅ Mejoras exitosas: {len(mejoras)}")
    
    for mejora in mejoras:
        print(f"  - {mejora['estrategia']}: {mejora['f1_score']:.4f}")

# ================================
# 2️⃣ PREDICCIONES MANUALES
# ================================

def ejemplo_predicciones_manuales():
    """Ejemplo de generar predicciones manualmente"""
    
    print("🔮 EJEMPLO: Predicciones manuales")
    print("="*40)
    
    import calcularf1_score as cf1
    
    # Entrenar modelo
    modelo, f1_train = cf1.entrenar_y_evaluar('train_local.csv')
    print(f"📊 F1 entrenamiento: {f1_train:.4f}")
    
    # Predecir en test_public (con target)
    pred_public, f1_public = cf1.obtenerscore('test_public.csv', modelo)
    print(f"🎯 F1 test public: {f1_public:.4f}")
    
    # Predecir en test_private (sin target)
    pred_private, _ = cf1.obtenerscore('test_private.csv', modelo)
    
    # Crear submission
    submission = cf1.crear_submission_final(
        pred_public, pred_private, 
        filename=f'submission_manual_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
    
    print(f"📝 Submission creado: {len(submission)} predicciones")

# ================================
# 3️⃣ SISTEMA AUTOMÁTICO
# ================================

def ejemplo_sistema_automatico():
    """Ejemplo de sistema automático completo"""
    
    print("🚀 EJEMPLO: Sistema automático")
    print("="*40)
    
    from api_submission_automatica import (
        configurar_credenciales, 
        AutoTrainingSystem,
        DatabaseManager
    )
    
    # 1. Configurar credenciales (solo una vez)
    # configurar_credenciales('tu_username', 'tu_api_key')
    
    # 2. Crear sistema automático
    # sistema = AutoTrainingSystem('tu_username', 'tu_api_key')
    
    # 3. Ejecutar un ciclo manual
    # sistema.ejecutar_ciclo_completo()
    
    # 4. Ver estadísticas
    db = DatabaseManager()
    stats = db.obtener_estadisticas()
    
    print(f"📊 Total submissions: {stats['total_submissions']}")
    print(f"📊 Mejor score: {stats['mejor_score_publico']}")
    
    print("💡 Para iniciar automático: sistema.iniciar_sistema_automatico()")

# ================================
# 4️⃣ CONFIGURACIÓN PERSONALIZADA
# ================================

def ejemplo_configuracion_personalizada():
    """Ejemplo de configuración personalizada"""
    
    print("⚙️ EJEMPLO: Configuración personalizada")
    print("="*40)
    
    import json
    
    # Cargar configuración actual
    with open('config/sistema_config.json', 'r') as f:
        config = json.load(f)
    
    print("📋 Configuración actual:")
    print(f"  Intervalo entrenamiento: {config['entrenamiento']['intervalo_horas']} horas")
    print(f"  Max submissions/día: {config['competencia']['max_submissions_per_day']}")
    print(f"  Mejora mínima: {config['competencia']['min_mejora_requerida']}")
    
    # Modificar configuración
    config['entrenamiento']['intervalo_horas'] = 6  # Cada 6 horas
    config['competencia']['min_mejora_requerida'] = 0.005  # Mejora mínima 0.5%
    
    # Guardar configuración modificada
    with open('config/sistema_config_personalizado.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuración personalizada guardada")

# ================================
# 5️⃣ MONITOREO Y ESTADÍSTICAS
# ================================

def ejemplo_monitoreo():
    """Ejemplo de monitoreo y estadísticas"""
    
    print("📊 EJEMPLO: Monitoreo y estadísticas")
    print("="*40)
    
    from api_submission_automatica import DatabaseManager
    
    db = DatabaseManager()
    stats = db.obtener_estadisticas()
    
    # Submissions
    df_submissions = stats['submissions']
    if len(df_submissions) > 0:
        print("📤 SUBMISSIONS:")
        print(f"  Total: {len(df_submissions)}")
        print(f"  Mejor score: {df_submissions['f1_score_publico'].max()}")
        print(f"  Promedio: {df_submissions['f1_score_publico'].mean():.4f}")
        
        print("\\n📈 Últimas 5 submissions:")
        for _, row in df_submissions.head(5).iterrows():
            print(f"  {row['timestamp']}: {row['f1_score_publico']:.4f}")
    
    # Entrenamientos
    df_entrenamientos = stats['entrenamientos']
    if len(df_entrenamientos) > 0:
        print("\\n🤖 ENTRENAMIENTOS:")
        print(f"  Total: {len(df_entrenamientos)}")
        print(f"  Mejor score: {df_entrenamientos['f1_score'].max():.4f}")
        
        print("\\n🏆 Mejores estrategias:")
        mejores = df_entrenamientos.nlargest(3, 'f1_score')
        for _, row in mejores.iterrows():
            print(f"  {row['estrategia_usada']}: {row['f1_score']:.4f}")

# ================================
# 🎮 MENÚ INTERACTIVO
# ================================

def menu_ejemplos():
    """Menú interactivo de ejemplos"""
    
    print("💡 EJEMPLOS DE USO - SISTEMA NEUROKUP II")
    print("="*50)
    
    ejemplos = {
        '1': ('Mejora manual de modelo', ejemplo_mejora_manual),
        '2': ('Predicciones manuales', ejemplo_predicciones_manuales),
        '3': ('Sistema automático', ejemplo_sistema_automatico),
        '4': ('Configuración personalizada', ejemplo_configuracion_personalizada),
        '5': ('Monitoreo y estadísticas', ejemplo_monitoreo),
    }
    
    while True:
        print("\\n📋 Ejemplos disponibles:")
        for key, (nombre, _) in ejemplos.items():
            print(f"  {key}️⃣ {nombre}")
        print("  0️⃣ Salir")
        
        opcion = input("\\nSelecciona un ejemplo (0-5): ").strip()
        
        if opcion == '0':
            break
        elif opcion in ejemplos:
            try:
                ejemplos[opcion][1]()
            except Exception as e:
                print(f"❌ Error ejecutando ejemplo: {e}")
        else:
            print("❌ Opción inválida")
    
    print("👋 ¡Gracias por usar los ejemplos!")

if __name__ == "__main__":
    menu_ejemplos()
'''
    
    with open('ejemplos_uso.py', 'w', encoding='utf-8') as f:
        f.write(ejemplo)
    
    print("✅ Ejemplos de uso creados: ejemplos_uso.py")

def setup_completo():
    """Ejecutar setup completo del sistema"""
    
    print("🚀 SETUP COMPLETO - SISTEMA AUTOMÁTICO NEUROKUP II")
    print("="*60)
    print("Este proceso configurará todo lo necesario para el sistema automático")
    print()
    
    try:
        # 1. Instalar dependencias
        instalar = input("¿Instalar dependencias de Python? (s/n): ").lower().strip()
        if instalar in ['s', 'si', 'sí', 'y', 'yes']:
            instalar_dependencias()
        
        # 2. Crear estructura
        crear_estructura_directorios()
        
        # 3. Crear archivos de configuración
        crear_archivo_configuracion()
        crear_archivo_requirements()
        crear_readme()
        crear_script_inicio()
        crear_ejemplo_uso()
        
        print("\n🎉 SETUP COMPLETO EXITOSO")
        print("="*60)
        print("📁 Archivos creados:")
        print("  ✅ inicio_rapido.py          # Script principal")
        print("  ✅ ejemplos_uso.py           # Ejemplos de uso")
        print("  ✅ requirements.txt          # Dependencias")
        print("  ✅ README.md                 # Documentación")
        print("  ✅ config/sistema_config.json # Configuración")
        print()
        print("📋 Próximos pasos:")
        print("  1️⃣ Coloca tus datasets (train_local.csv, test_public.csv, test_private.csv)")
        print("  2️⃣ Ejecuta: python inicio_rapido.py")
        print("  3️⃣ Configura credenciales de Kaggle")
        print("  4️⃣ ¡Inicia el sistema automático!")
        print()
        print("🎯 ¡Todo listo para la competencia NeuroKup II!")
        
    except Exception as e:
        print(f"❌ Error en setup: {e}")
        print("💡 Revisa los permisos y dependencias")

if __name__ == "__main__":
    setup_completo()