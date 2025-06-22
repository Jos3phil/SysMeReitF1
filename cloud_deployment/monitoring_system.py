# ================================
# 📊 SISTEMA DE MONITOREO Y NOTIFICACIONES
# ================================
# Monitoreo robusto con alertas inteligentes

import psutil
import sqlite3
import json
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pathlib import Path
from production_config import ProductionConfig

class SystemMonitor:
    """Monitoreo del sistema en tiempo real"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.alerts_sent = {}
        
    def collect_metrics(self):
        """Recopilar métricas del sistema"""
        try:
            # Métricas de CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de red
            network = psutil.net_io_counters()
            
            # Métricas del proceso actual
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / 1024**3,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / 1024**3,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'process_memory_mb': process_memory,
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
            
            # Guardar en historial
            self.metrics_history.append(metrics)
            
            # Mantener solo las últimas 1000 métricas
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error recopilando métricas: {e}")
            return {}
    
    def health_check(self):
        """Verificar salud del sistema"""
        issues = []
        
        try:
            # Verificar uso de memoria
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append(f"Memoria alta: {memory.percent:.1f}%")
            
            # Verificar uso de CPU
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 95:
                issues.append(f"CPU alta: {cpu:.1f}%")
            
            # Verificar espacio en disco
            disk = psutil.disk_usage('/')
            if disk.percent > 85:
                issues.append(f"Disco lleno: {disk.percent:.1f}%")
            
            # Verificar archivos críticos
            critical_files = [
                ProductionConfig.DB_PATH,
                ProductionConfig.BASE_DIR / '.env'
            ]
            
            for file_path in critical_files:
                if not file_path.exists():
                    issues.append(f"Archivo crítico faltante: {file_path}")
            
            # Verificar conectividad de Kaggle
            try:
                import kaggle
                kaggle.api.authenticate()
            except Exception:
                issues.append("Credenciales de Kaggle inválidas")
            
            return {
                'healthy': len(issues) == 0,
                'issues': issues,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error en health check: {e}")
            return {
                'healthy': False,
                'issues': [f"Error en health check: {e}"],
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_summary(self):
        """Obtener resumen del sistema"""
        if not self.metrics_history:
            return "No hay métricas disponibles"
        
        latest = self.metrics_history[-1]
        
        summary = f"""
🖥️ **RESUMEN DEL SISTEMA**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Métricas actuales:**
• CPU: {latest['cpu_percent']:.1f}%
• Memoria: {latest['memory_percent']:.1f}% ({latest['memory_available_gb']:.1f}GB disponible)
• Disco: {latest['disk_percent']:.1f}% ({latest['disk_free_gb']:.1f}GB libre)
• Proceso: {latest['process_memory_mb']:.1f}MB

⏰ **Timestamp:** {latest['timestamp']}

📈 **Estadísticas (últimas 24h):**
• Métricas recopiladas: {len(self.metrics_history)}
• CPU promedio: {sum(m['cpu_percent'] for m in self.metrics_history[-144:]) / len(self.metrics_history[-144:]):.1f}%
• Memoria promedio: {sum(m['memory_percent'] for m in self.metrics_history[-144:]) / len(self.metrics_history[-144:]):.1f}%
"""
        return summary

class NotificationManager:
    """Gestión de notificaciones (email, Slack, etc.)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def send_notification(self, title, message, priority='normal'):
        """Enviar notificación por todos los canales configurados"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"[{timestamp}] {message}"
        
        # Log local
        if priority == 'critical':
            self.logger.critical(f"{title}: {message}")
        elif priority == 'warning':
            self.logger.warning(f"{title}: {message}")
        else:
            self.logger.info(f"{title}: {message}")
        
        # Email
        if ProductionConfig.EMAIL_ENABLED:
            self._send_email(title, full_message, priority)
        
        # Slack
        if ProductionConfig.SLACK_ENABLED:
            self._send_slack(title, full_message, priority)
    
    def _send_email(self, title, message, priority):
        """Enviar notificación por email"""
        try:
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = ProductionConfig.EMAIL_USER
            msg['To'] = ProductionConfig.ADMIN_EMAIL
            msg['Subject'] = f"[NeuroKup II] {title}"
            
            # Agregar prioridad al subject
            if priority == 'critical':
                msg['Subject'] = f"🚨 [CRÍTICO] {msg['Subject']}"
            elif priority == 'warning':
                msg['Subject'] = f"⚠️ [ALERTA] {msg['Subject']}"
            
            # Cuerpo del mensaje
            body = f"""
Sistema: NeuroKup II Automation
Servidor: {ProductionConfig.BASE_DIR}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Mensaje:
{message}

---
Este es un mensaje automático del sistema de monitoreo.
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(ProductionConfig.SMTP_SERVER, ProductionConfig.SMTP_PORT)
            server.starttls()
            server.login(ProductionConfig.EMAIL_USER, ProductionConfig.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(ProductionConfig.EMAIL_USER, ProductionConfig.ADMIN_EMAIL, text)
            server.quit()
            
            self.logger.info(f"Email enviado: {title}")
            
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
    
    def _send_slack(self, title, message, priority):
        """Enviar notificación a Slack"""
        try:
            # Determinar emoji y color según prioridad
            if priority == 'critical':
                emoji = "🚨"
                color = "#FF0000"
            elif priority == 'warning':
                emoji = "⚠️"
                color = "#FFA500"
            else:
                emoji = "ℹ️"
                color = "#36a64f"
            
            # Crear payload
            payload = {
                "text": f"{emoji} {title}",
                "attachments": [{
                    "color": color,
                    "fields": [
                        {
                            "title": "Servidor",
                            "value": str(ProductionConfig.BASE_DIR),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "short": True
                        },
                        {
                            "title": "Mensaje",
                            "value": message,
                            "short": False
                        }
                    ]
                }]
            }
            
            # Enviar a Slack
            response = requests.post(
                ProductionConfig.SLACK_WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Slack enviado: {title}")
            else:
                self.logger.error(f"Error en Slack: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error enviando Slack: {e}")

class AlertManager:
    """Gestión inteligente de alertas para evitar spam"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_history = {}
        self.cooldown_periods = {
            'high_cpu': timedelta(minutes=15),
            'high_memory': timedelta(minutes=15),
            'disk_full': timedelta(hours=1),
            'model_error': timedelta(minutes=30),
            'kaggle_error': timedelta(minutes=60)
        }
    
    def should_send_alert(self, alert_type):
        """Determinar si se debe enviar una alerta basado en cooldown"""
        now = datetime.now()
        
        if alert_type not in self.alert_history:
            self.alert_history[alert_type] = now
            return True
        
        last_alert = self.alert_history[alert_type]
        cooldown = self.cooldown_periods.get(alert_type, timedelta(minutes=30))
        
        if now - last_alert >= cooldown:
            self.alert_history[alert_type] = now
            return True
        
        return False
    
    def reset_alert(self, alert_type):
        """Resetear historial de alerta (cuando el problema se resuelve)"""
        if alert_type in self.alert_history:
            del self.alert_history[alert_type]

class MetricsDatabase:
    """Base de datos para almacenar métricas históricas"""
    
    def __init__(self):
        self.db_path = ProductionConfig.BASE_DIR / 'data' / 'metrics.db'
        self.logger = logging.getLogger(__name__)
        self._init_db()
    
    def _init_db(self):
        """Inicializar base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_bytes_sent INTEGER,
                    network_bytes_recv INTEGER,
                    process_memory_mb REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error inicializando DB de métricas: {e}")
    
    def save_metrics(self, metrics):
        """Guardar métricas en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO metrics (
                    timestamp, cpu_percent, memory_percent, disk_percent,
                    network_bytes_sent, network_bytes_recv, process_memory_mb
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics['timestamp'],
                metrics['cpu_percent'],
                metrics['memory_percent'], 
                metrics['disk_percent'],
                metrics['network_bytes_sent'],
                metrics['network_bytes_recv'],
                metrics['process_memory_mb']
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando métricas: {e}")
    
    def get_metrics_summary(self, hours=24):
        """Obtener resumen de métricas de las últimas N horas"""
        try:
            since = datetime.now() - timedelta(hours=hours)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT 
                    AVG(cpu_percent) as avg_cpu,
                    MAX(cpu_percent) as max_cpu,
                    AVG(memory_percent) as avg_memory,
                    MAX(memory_percent) as max_memory,
                    COUNT(*) as data_points
                FROM metrics 
                WHERE timestamp > ?
            ''', (since.isoformat(),))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'avg_cpu': result[0] or 0,
                'max_cpu': result[1] or 0,
                'avg_memory': result[2] or 0,
                'max_memory': result[3] or 0,
                'data_points': result[4] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de métricas: {e}")
            return {}

if __name__ == "__main__":
    # Test del sistema de monitoreo
    monitor = SystemMonitor()
    notifier = NotificationManager()
    
    print("🧪 Testing sistema de monitoreo...")
    
    # Test métricas
    metrics = monitor.collect_metrics()
    print(f"✅ Métricas: {metrics}")
    
    # Test health check
    health = monitor.health_check()
    print(f"✅ Health check: {health}")
    
    # Test notificación
    notifier.send_notification("Test", "Sistema de monitoreo funcionando correctamente")
    print("✅ Test completado")
