# ================================
# 🚀 SISTEMA PRINCIPAL PARA PRODUCCIÓN
# ================================
# Orquestador principal con monitoreo robusto

import sys
import time
import signal
import logging
import threading
from datetime import datetime, timedelta
import psutil
import json
from pathlib import Path

# Imports del sistema
sys.path.append(str(Path(__file__).parent))
from production_config import ProductionConfig, setup_logging, SecurityManager
from monitoring_system import SystemMonitor, NotificationManager
from backup_manager import BackupManager

# Imports de ML
sys.path.append(str(Path(__file__).parent.parent))
from automatizacion import calcularf1_score, mejora_iterativa, api_submission_automatica

class ProductionSystem:
    """Sistema principal para ejecutar en producción"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.running = False
        self.threads = {}
        self.monitor = SystemMonitor()
        self.notifier = NotificationManager()
        self.backup_manager = BackupManager()
        
        # Validar configuración
        ProductionConfig.validate_config()
        SecurityManager.setup_file_permissions()
        
        self.logger.info("🚀 Sistema de producción inicializado")
    
    def signal_handler(self, signum, frame):
        """Manejar señales del sistema (SIGTERM, SIGINT)"""
        self.logger.info(f"Señal {signum} recibida. Iniciando apagado graceful...")
        self.stop()
    
    def start(self):
        """Iniciar el sistema completo"""
        try:
            self.logger.info("🎯 Iniciando sistema de producción...")
            
            # Registrar manejadores de señales
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            
            self.running = True
            
            # Validar credenciales antes de empezar
            if not SecurityManager.validate_kaggle_credentials():
                raise Exception("Credenciales de Kaggle inválidas")
            
            # Iniciar threads del sistema
            self._start_monitoring_thread()
            self._start_ml_pipeline_thread()
            self._start_backup_thread()
            self._start_health_check_thread()
            
            self.logger.info("✅ Todos los sistemas iniciados correctamente")
            
            # Notificar inicio
            self.notifier.send_notification(
                "🚀 Sistema NeuroKup II iniciado", 
                "El sistema de ML automático está funcionando correctamente."
            )
            
            # Loop principal
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Error crítico en el sistema: {e}")
            self.notifier.send_notification(
                "🚨 Error crítico en sistema", 
                f"El sistema se ha detenido debido a: {e}"
            )
            self.stop()
            sys.exit(1)
    
    def _main_loop(self):
        """Loop principal del sistema"""
        while self.running:
            try:
                # Verificar estado de threads
                for thread_name, thread in self.threads.items():
                    if not thread.is_alive():
                        self.logger.warning(f"Thread {thread_name} se ha detenido")
                        self.notifier.send_notification(
                            f"⚠️ Thread {thread_name} detenido",
                            "Se intentará reiniciar automáticamente."
                        )
                
                # Dormir y verificar cada minuto
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("Interrupción de teclado recibida")
                break
            except Exception as e:
                self.logger.error(f"Error en loop principal: {e}")
                time.sleep(60)
    
    def _start_monitoring_thread(self):
        """Iniciar thread de monitoreo del sistema"""
        def monitoring_loop():
            while self.running:
                try:
                    metrics = self.monitor.collect_metrics()
                    
                    # Verificar umbrales críticos
                    if metrics['memory_percent'] > ProductionConfig.MAX_MEMORY_MB:
                        self.logger.warning(f"Uso de memoria alto: {metrics['memory_percent']:.1f}%")
                    
                    if metrics['cpu_percent'] > ProductionConfig.MAX_CPU_PERCENT:
                        self.logger.warning(f"Uso de CPU alto: {metrics['cpu_percent']:.1f}%")
                    
                    # Log métricas cada hora
                    if datetime.now().minute == 0:
                        self.logger.info(f"Métricas del sistema: {metrics}")
                    
                    time.sleep(ProductionConfig.HEALTH_CHECK_INTERVAL)
                    
                except Exception as e:
                    self.logger.error(f"Error en monitoreo: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitoring_loop, name="monitoring")
        thread.daemon = True
        thread.start()
        self.threads['monitoring'] = thread
        self.logger.info("✅ Thread de monitoreo iniciado")
    
    def _start_ml_pipeline_thread(self):
        """Iniciar thread del pipeline de ML"""
        def ml_pipeline_loop():
            last_training = datetime.now() - timedelta(hours=24)  # Forzar entrenamiento inicial
            
            while self.running:
                try:
                    # Verificar si es hora de entrenar
                    if datetime.now() - last_training >= timedelta(hours=ProductionConfig.TRAINING_INTERVAL_HOURS):
                        self.logger.info("🧠 Iniciando ciclo de entrenamiento...")
                        
                        # Ejecutar mejora iterativa
                        resultado = mejora_iterativa.mejorar_modelo_automatico()
                        
                        if resultado and resultado.get('mejora_obtenida', 0) > ProductionConfig.MIN_IMPROVEMENT_THRESHOLD:
                            self.logger.info(f"✅ Mejora obtenida: {resultado['mejora_obtenida']:.4f}")
                            
                            # Intentar submission automática
                            submission_result = api_submission_automatica.ejecutar_submission_automatica()
                            
                            if submission_result:
                                self.notifier.send_notification(
                                    "🎯 Nueva submission realizada",
                                    f"Mejora: {resultado['mejora_obtenida']:.4f}"
                                )
                        
                        last_training = datetime.now()
                    
                    # Verificar cada 30 minutos
                    time.sleep(ProductionConfig.VERIFICATION_INTERVAL_MINUTES * 60)
                    
                except Exception as e:
                    self.logger.error(f"Error en pipeline ML: {e}")
                    time.sleep(300)  # Esperar 5 minutos antes de reintentar
        
        thread = threading.Thread(target=ml_pipeline_loop, name="ml_pipeline")
        thread.daemon = True
        thread.start()
        self.threads['ml_pipeline'] = thread
        self.logger.info("✅ Thread de ML pipeline iniciado")
    
    def _start_backup_thread(self):
        """Iniciar thread de backups automáticos"""
        def backup_loop():
            while self.running:
                try:
                    # Backup cada 24 horas
                    self.backup_manager.create_backup()
                    time.sleep(ProductionConfig.BACKUP_INTERVAL_HOURS * 3600)
                    
                except Exception as e:
                    self.logger.error(f"Error en backup: {e}")
                    time.sleep(3600)  # Reintentar en 1 hora
        
        thread = threading.Thread(target=backup_loop, name="backup")
        thread.daemon = True
        thread.start()
        self.threads['backup'] = thread
        self.logger.info("✅ Thread de backup iniciado")
    
    def _start_health_check_thread(self):
        """Iniciar thread de health checks"""
        def health_check_loop():
            while self.running:
                try:
                    health_status = self.monitor.health_check()
                    
                    if not health_status['healthy']:
                        self.logger.warning(f"Health check fallido: {health_status['issues']}")
                        self.notifier.send_notification(
                            "⚠️ Health check fallido",
                            f"Problemas detectados: {', '.join(health_status['issues'])}"
                        )
                    
                    time.sleep(300)  # Cada 5 minutos
                    
                except Exception as e:
                    self.logger.error(f"Error en health check: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=health_check_loop, name="health_check")
        thread.daemon = True
        thread.start()
        self.threads['health_check'] = thread
        self.logger.info("✅ Thread de health check iniciado")
    
    def stop(self):
        """Detener el sistema gracefully"""
        self.logger.info("🛑 Deteniendo sistema...")
        self.running = False
        
        # Esperar a que los threads terminen
        for thread_name, thread in self.threads.items():
            self.logger.info(f"Esperando thread {thread_name}...")
            thread.join(timeout=30)
        
        # Backup final
        try:
            self.backup_manager.create_backup()
            self.logger.info("✅ Backup final completado")
        except Exception as e:
            self.logger.error(f"Error en backup final: {e}")
        
        self.logger.info("✅ Sistema detenido correctamente")

def main():
    """Función principal"""
    try:
        system = ProductionSystem()
        system.start()
    except KeyboardInterrupt:
        print("\n🛑 Interrupción recibida. Deteniendo sistema...")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
