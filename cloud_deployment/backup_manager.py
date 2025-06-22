# ================================
# 💾 SISTEMA DE BACKUPS AUTOMÁTICOS
# ================================
# Backup robusto de modelos, datos y configuraciones

import os
import shutil
import sqlite3
import tarfile
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from production_config import ProductionConfig

class BackupManager:
    """Gestión de backups automáticos y restauración"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backup_dir = ProductionConfig.BACKUPS_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de AWS S3 (opcional)
        self.s3_enabled = os.getenv('S3_BACKUP_ENABLED', 'False').lower() == 'true'
        self.s3_bucket = os.getenv('S3_BACKUP_BUCKET')
        self.s3_client = None
        
        if self.s3_enabled and self.s3_bucket:
            self._init_s3_client()
    
    def _init_s3_client(self):
        """Inicializar cliente de S3"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Verificar que el bucket existe
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            self.logger.info(f"✅ Conectado a S3 bucket: {self.s3_bucket}")
            
        except Exception as e:
            self.logger.error(f"Error configurando S3: {e}")
            self.s3_enabled = False
    
    def create_backup(self):
        """Crear backup completo del sistema"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"neurokup_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        try:
            self.logger.info(f"🗄️ Creando backup: {backup_name}")
            
            # Crear archivo tar
            with tarfile.open(backup_path, 'w:gz') as tar:
                
                # Backup de modelos
                models_dir = ProductionConfig.MODELS_DIR
                if models_dir.exists():
                    tar.add(models_dir, arcname='models')
                    self.logger.info("✅ Modelos respaldados")
                
                # Backup de base de datos
                db_path = ProductionConfig.DB_PATH
                if db_path.exists():
                    tar.add(db_path, arcname='data/submissions.db')
                    self.logger.info("✅ Base de datos respaldada")
                
                # Backup de configuración
                config_files = [
                    ProductionConfig.BASE_DIR / '.env',
                    ProductionConfig.BASE_DIR / 'config' / 'sistema_config.json'
                ]
                
                for config_file in config_files:
                    if config_file.exists():
                        tar.add(config_file, arcname=f'config/{config_file.name}')
                
                # Backup de submissions recientes
                submissions_dir = ProductionConfig.SUBMISSIONS_DIR
                if submissions_dir.exists():
                    # Solo los últimos 30 archivos de submission
                    submission_files = sorted(
                        submissions_dir.glob('*.csv'),
                        key=lambda x: x.stat().st_mtime,
                        reverse=True
                    )[:30]
                    
                    for sub_file in submission_files:
                        tar.add(sub_file, arcname=f'submissions/{sub_file.name}')
                
                # Backup de logs recientes (últimos 7 días)
                logs_dir = ProductionConfig.LOGS_DIR
                if logs_dir.exists():
                    cutoff_date = datetime.now() - timedelta(days=7)
                    for log_file in logs_dir.glob('*.log*'):
                        if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff_date:
                            tar.add(log_file, arcname=f'logs/{log_file.name}')
            
            # Verificar integridad del backup
            if self._verify_backup(backup_path):
                self.logger.info(f"✅ Backup creado exitosamente: {backup_path}")
                
                # Subir a S3 si está configurado
                if self.s3_enabled:
                    self._upload_to_s3(backup_path, backup_name)
                
                # Limpiar backups antiguos
                self._cleanup_old_backups()
                
                return {
                    'success': True,
                    'backup_path': str(backup_path),
                    'backup_name': backup_name,
                    'size_mb': backup_path.stat().st_size / 1024 / 1024
                }
            else:
                self.logger.error(f"❌ Backup corrupto: {backup_path}")
                backup_path.unlink(missing_ok=True)
                return {'success': False, 'error': 'Backup corrupto'}
                
        except Exception as e:
            self.logger.error(f"❌ Error creando backup: {e}")
            return {'success': False, 'error': str(e)}
    
    def _verify_backup(self, backup_path):
        """Verificar integridad del backup"""
        try:
            with tarfile.open(backup_path, 'r:gz') as tar:
                # Verificar que el archivo se puede leer
                members = tar.getmembers()
                self.logger.info(f"Backup contiene {len(members)} archivos")
                
                # Verificar algunos archivos críticos
                critical_files = ['models/', 'data/submissions.db']
                found_critical = [name for name in tar.getnames() if any(cf in name for cf in critical_files)]
                
                if found_critical:
                    self.logger.info(f"Archivos críticos encontrados: {found_critical}")
                    return True
                else:
                    self.logger.warning("No se encontraron archivos críticos en el backup")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error verificando backup: {e}")
            return False
    
    def _upload_to_s3(self, backup_path, backup_name):
        """Subir backup a S3"""
        try:
            s3_key = f"neurokup-backups/{backup_name}.tar.gz"
            
            self.logger.info(f"☁️ Subiendo backup a S3: {s3_key}")
            self.s3_client.upload_file(
                str(backup_path),
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    'StorageClass': 'STANDARD_IA',  # Almacenamiento más barato
                    'ServerSideEncryption': 'AES256'  # Encriptación
                }
            )
            
            self.logger.info(f"✅ Backup subido a S3: s3://{self.s3_bucket}/{s3_key}")
            
        except Exception as e:
            self.logger.error(f"Error subiendo a S3: {e}")
    
    def _cleanup_old_backups(self):
        """Limpiar backups antiguos (mantener últimos 7 locales, 30 en S3)"""
        try:
            # Limpiar backups locales
            backup_files = sorted(
                self.backup_dir.glob('neurokup_backup_*.tar.gz'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Mantener solo los últimos 7
            for old_backup in backup_files[7:]:
                old_backup.unlink()
                self.logger.info(f"🗑️ Backup local eliminado: {old_backup.name}")
            
            # Limpiar backups en S3
            if self.s3_enabled:
                self._cleanup_s3_backups()
                
        except Exception as e:
            self.logger.error(f"Error limpiando backups: {e}")
    
    def _cleanup_s3_backups(self):
        """Limpiar backups antiguos en S3"""
        try:
            # Listar objetos en S3
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix='neurokup-backups/'
            )
            
            if 'Contents' in response:
                # Ordenar por fecha
                objects = sorted(
                    response['Contents'],
                    key=lambda x: x['LastModified'],
                    reverse=True
                )
                
                # Eliminar los más antiguos (mantener 30)
                for old_object in objects[30:]:
                    self.s3_client.delete_object(
                        Bucket=self.s3_bucket,
                        Key=old_object['Key']
                    )
                    self.logger.info(f"🗑️ Backup S3 eliminado: {old_object['Key']}")
                    
        except Exception as e:
            self.logger.error(f"Error limpiando S3: {e}")
    
    def restore_backup(self, backup_name_or_path):
        """Restaurar desde un backup"""
        try:
            # Determinar ruta del backup
            if isinstance(backup_name_or_path, str) and not backup_name_or_path.endswith('.tar.gz'):
                backup_path = self.backup_dir / f"{backup_name_or_path}.tar.gz"
            else:
                backup_path = Path(backup_name_or_path)
            
            if not backup_path.exists():
                # Intentar descargar desde S3
                if self.s3_enabled:
                    s3_key = f"neurokup-backups/{backup_path.name}"
                    self.s3_client.download_file(self.s3_bucket, s3_key, str(backup_path))
                    self.logger.info(f"✅ Backup descargado desde S3")
                else:
                    raise FileNotFoundError(f"Backup no encontrado: {backup_path}")
            
            self.logger.info(f"🔄 Restaurando backup: {backup_path}")
            
            # Crear backup de seguridad del estado actual
            current_backup = self.create_backup()
            self.logger.info(f"🛡️ Backup de seguridad creado: {current_backup.get('backup_name', 'N/A')}")
            
            # Extraer backup
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(ProductionConfig.BASE_DIR)
            
            self.logger.info(f"✅ Backup restaurado exitosamente")
            return {'success': True, 'restored_from': str(backup_path)}
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando backup: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_backups(self):
        """Listar backups disponibles"""
        backups = {
            'local': [],
            's3': []
        }
        
        try:
            # Backups locales
            for backup_file in sorted(self.backup_dir.glob('neurokup_backup_*.tar.gz')):
                stat = backup_file.stat()
                backups['local'].append({
                    'name': backup_file.stem,
                    'path': str(backup_file),
                    'size_mb': stat.st_size / 1024 / 1024,
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            # Backups en S3
            if self.s3_enabled:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix='neurokup-backups/'
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        backups['s3'].append({
                            'name': obj['Key'].split('/')[-1].replace('.tar.gz', ''),
                            'key': obj['Key'],
                            'size_mb': obj['Size'] / 1024 / 1024,
                            'created': obj['LastModified'].isoformat()
                        })
            
        except Exception as e:
            self.logger.error(f"Error listando backups: {e}")
        
        return backups
    
    def create_database_backup(self):
        """Crear backup específico de la base de datos con dump SQL"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"db_backup_{timestamp}.sql"
        
        try:
            conn = sqlite3.connect(ProductionConfig.DB_PATH)
            
            with open(backup_file, 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
            
            conn.close()
            
            self.logger.info(f"✅ Backup de DB creado: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Error en backup de DB: {e}")
            return None

def create_backup_schedule():
    """Configurar schedule de backups automáticos"""
    import schedule
    
    backup_manager = BackupManager()
    
    # Backup completo diario a las 3 AM
    schedule.every().day.at("03:00").do(backup_manager.create_backup)
    
    # Backup de DB cada 6 horas
    schedule.every(6).hours.do(backup_manager.create_database_backup)
    
    logging.info("📅 Schedule de backups configurado")

if __name__ == "__main__":
    # Test del sistema de backup
    backup_manager = BackupManager()
    
    print("🧪 Testing sistema de backup...")
    
    # Test crear backup
    result = backup_manager.create_backup()
    print(f"✅ Backup creado: {result}")
    
    # Test listar backups
    backups = backup_manager.list_backups()
    print(f"✅ Backups disponibles: {len(backups['local'])} locales, {len(backups['s3'])} en S3")
    
    print("✅ Test completado")
