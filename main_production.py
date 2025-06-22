# ================================
# 🚀 ARCHIVO PRINCIPAL MEJORADO PARA PRODUCCIÓN
# ================================
# Version optimizada que integra todos los sistemas

import sys
import os
from pathlib import Path

# Agregar paths necesarios
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.extend([str(current_dir), str(project_root)])

# Imports del sistema de producción
from cloud_deployment.production_config import ProductionConfig, setup_logging
from cloud_deployment.main import ProductionSystem

def main():
    """
    Función principal optimizada para producción
    
    Esta función:
    1. Configura el sistema de producción
    2. Inicia todos los servicios
    3. Maneja errores gracefully
    4. Proporciona logging robusto
    """
    
    try:
        # Configurar logging
        logger = setup_logging()
        logger.info("🚀 Iniciando NeuroKup II Production System")
        
        # Validar configuración
        ProductionConfig.validate_config()
        logger.info("✅ Configuración validada")
        
        # Crear e iniciar sistema de producción
        system = ProductionSystem()
        system.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupción de usuario - Cerrando sistema gracefully")
        
    except Exception as e:
        logger.critical(f"❌ Error crítico en el sistema: {e}")
        sys.exit(1)
        
    finally:
        logger.info("🏁 Sistema finalizado")

if __name__ == "__main__":
    main()
