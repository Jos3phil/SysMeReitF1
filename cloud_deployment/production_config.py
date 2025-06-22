# ================================
# 🔐 CONFIGURACIÓN SEGURA PARA PRODUCCIÓN
# ================================
# Variables de entorno y configuración para AWS EC2

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ProductionConfig:
    """Configuración para entorno de producción"""
    
    # === CONFIGURACIÓN BÁSICA ===
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
    
    # === DIRECTORIOS ===
    BASE_DIR = Path(os.getenv('BASE_DIR', '/home/ubuntu/neurokup-system'))
    LOGS_DIR = BASE_DIR / 'logs'
    DATA_DIR = BASE_DIR / 'data' 
    MODELS_DIR = BASE_DIR / 'models'
    SUBMISSIONS_DIR = BASE_DIR / 'submissions'
    BACKUPS_DIR = BASE_DIR / 'backups'
    
    # === KAGGLE CREDENTIALS ===
    KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME')
    KAGGLE_KEY = os.getenv('KAGGLE_KEY')
    
    # === COMPETITION CONFIG ===
    COMPETITION_NAME = os.getenv('COMPETITION_NAME', 'neuro-kup-ii-beta-acm-ai')
    MAX_SUBMISSIONS_PER_DAY = int(os.getenv('MAX_SUBMISSIONS_PER_DAY', '7'))
    MIN_IMPROVEMENT_THRESHOLD = float(os.getenv('MIN_IMPROVEMENT_THRESHOLD', '0.001'))
    
    # === TIMING CONFIGURATION ===
    TRAINING_INTERVAL_HOURS = int(os.getenv('TRAINING_INTERVAL_HOURS', '4'))
    VERIFICATION_INTERVAL_MINUTES = int(os.getenv('VERIFICATION_INTERVAL_MINUTES', '30'))
    BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
    
    # === DATABASE ===
    DB_PATH = BASE_DIR / 'data' / 'submissions.db'
    DB_BACKUP_COUNT = int(os.getenv('DB_BACKUP_COUNT', '7'))
    
    # === LOGGING ===
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # === MONITORING ===
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '300'))  # 5 min
    MAX_MEMORY_MB = int(os.getenv('MAX_MEMORY_MB', '2048'))
    MAX_CPU_PERCENT = int(os.getenv('MAX_CPU_PERCENT', '80'))
    
    # === EMAIL NOTIFICATIONS (opcional) ===
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    
    # === SLACK NOTIFICATIONS (opcional) ===
    SLACK_ENABLED = os.getenv('SLACK_ENABLED', 'False').lower() == 'true'
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    
    @classmethod
    def validate_config(cls):
        """Validar configuración crítica"""
        errors = []
        
        # Validar Kaggle credentials
        if not cls.KAGGLE_USERNAME or not cls.KAGGLE_KEY:
            errors.append("KAGGLE_USERNAME y KAGGLE_KEY son requeridos")
        
        # Validar directorios
        for dir_path in [cls.DATA_DIR, cls.MODELS_DIR, cls.LOGS_DIR, 
                        cls.SUBMISSIONS_DIR, cls.BACKUPS_DIR]:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logging.info(f"Directorio creado: {dir_path}")
                except Exception as e:
                    errors.append(f"No se puede crear directorio {dir_path}: {e}")
        
        if errors:
            raise ValueError(f"Errores de configuración: {'; '.join(errors)}")
        
        return True

def setup_logging():
    """Configurar logging para producción"""
    from logging.handlers import RotatingFileHandler
    
    # Crear directorio de logs si no existe
    ProductionConfig.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configurar logging
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        ProductionConfig.LOGS_DIR / 'neurokup.log',
        maxBytes=ProductionConfig.LOG_MAX_BYTES,
        backupCount=ProductionConfig.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(logging.Formatter(ProductionConfig.LOG_FORMAT))
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(ProductionConfig.LOG_FORMAT))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def create_env_template():
    """Crear archivo .env template"""
    template = """# ================================
# 🔐 CONFIGURACIÓN DE ENTORNO - NEUROKUP II
# ================================

# === CONFIGURACIÓN BÁSICA ===
DEBUG=False
ENVIRONMENT=production
BASE_DIR=/home/ubuntu/neurokup-system

# === KAGGLE CREDENTIALS ===
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

# === COMPETITION ===
COMPETITION_NAME=neuro-kup-ii-beta-acm-ai
MAX_SUBMISSIONS_PER_DAY=7
MIN_IMPROVEMENT_THRESHOLD=0.001

# === TIMING ===
TRAINING_INTERVAL_HOURS=4
VERIFICATION_INTERVAL_MINUTES=30
BACKUP_INTERVAL_HOURS=24

# === LOGGING ===
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# === MONITORING ===
HEALTH_CHECK_INTERVAL=300
MAX_MEMORY_MB=2048
MAX_CPU_PERCENT=80

# === EMAIL NOTIFICATIONS (opcional) ===
EMAIL_ENABLED=False
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
ADMIN_EMAIL=admin@example.com

# === SLACK NOTIFICATIONS (opcional) ===
SLACK_ENABLED=False
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
"""
    
    env_path = ProductionConfig.BASE_DIR / '.env'
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(template)
        logging.info(f"Archivo .env template creado en {env_path}")
    
    return env_path

class SecurityManager:
    """Gestión de seguridad para el sistema"""
    
    @staticmethod
    def setup_file_permissions():
        """Configurar permisos de archivos sensibles"""
        import stat
        
        # Archivos sensibles
        sensitive_files = [
            ProductionConfig.BASE_DIR / '.env',
            ProductionConfig.BASE_DIR / 'kaggle.json'
        ]
        
        for file_path in sensitive_files:
            if file_path.exists():
                # Solo el propietario puede leer/escribir
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
                logging.info(f"Permisos configurados para {file_path}")
    
    @staticmethod
    def validate_kaggle_credentials():
        """Validar que las credenciales de Kaggle funcionen"""
        try:
            import kaggle
            kaggle.api.authenticate()
            # Intentar obtener lista de competencias
            competitions = kaggle.api.competitions_list(page=1)
            logging.info("✅ Credenciales de Kaggle válidas")
            return True
        except Exception as e:
            logging.error(f"❌ Error en credenciales de Kaggle: {e}")
            return False

if __name__ == "__main__":
    # Ejecutar cuando se importe el módulo
    try:
        ProductionConfig.validate_config()
        setup_logging()
        create_env_template()
        SecurityManager.setup_file_permissions()
        SecurityManager.validate_kaggle_credentials()
        print("✅ Configuración de producción inicializada correctamente")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        exit(1)
