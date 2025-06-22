# ================================
# 🤖 API DE SUBMISSION AUTOMÁTICA PARA NEUROKUP II
# ================================
# Sistema completo de entrenamiento continuo y submissions automáticas

import requests
import sqlite3
import pandas as pd
import numpy as np
import json
import time
import logging
import schedule
import threading
from datetime import datetime, timedelta
import os
import hashlib
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Imports de ML
import automatizacion.calcularf1_score as calcularf1_score
from mejora_iterativa import mejorar_modelo_automatico

# ================================
# 🔧 CONFIGURACIÓN
# ================================

class Config:
    """Configuración del sistema de submissions automáticas"""
    
    # Configuración de la competencia
    COMPETITION_URL = "https://www.kaggle.com/competitions/neuro-kup-ii-beta-acm-ai"
    API_BASE_URL = "https://www.kaggle.com/api/v1"
    
    # Límites de submissions
    MAX_SUBMISSIONS_PER_DAY = 7
    MIN_MEJORA_REQUERIDA = 0.001  # Mejora mínima para subir
    
    # Archivos de configuración
    DB_FILE = "submissions_db.sqlite"
    CONFIG_FILE = "api_config.json"
    LOG_FILE = "submissions.log"
    CREDENTIALS_FILE = "kaggle_credentials.json"
    
    # Intervalos de tiempo
    ENTRENAMIENTO_INTERVALO_HORAS = 4
    VERIFICACION_INTERVALO_MINUTOS = 30
    
    # Directorios
    MODELS_DIR = "models_backup"
    SUBMISSIONS_DIR = "submissions_backup"

class NeuroKupAPI:
    """Cliente API para interactuar con NeuroKup II"""
    
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key
        self.session = requests.Session()
        self.session.auth = (username, api_key)
        
        # Configurar logging
        logging.basicConfig(
            filename=Config.LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Crear directorios
        Path(Config.MODELS_DIR).mkdir(exist_ok=True)
        Path(Config.SUBMISSIONS_DIR).mkdir(exist_ok=True)
        
        self.logger.info("🚀 NeuroKupAPI inicializada")
    
    def verificar_conexion(self):
        """Verificar conexión con la API de Kaggle"""
        
        try:
            # Endpoint de verificación (ajustar según API real)
            response = self.session.get(f"{Config.API_BASE_URL}/competitions/list")
            
            if response.status_code == 200:
                self.logger.info("✅ Conexión con API verificada")
                return True
            else:
                self.logger.error(f"❌ Error de conexión: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error verificando conexión: {e}")
            return False
    
    def obtener_info_competencia(self):
        """Obtener información de la competencia"""
        
        try:
            # Endpoint específico de la competencia (ajustar según API real)
            url = f"{Config.API_BASE_URL}/competitions/neuro-kup-ii-beta-acm-ai"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'deadline': data.get('deadline'),
                    'submissions_today': data.get('submissions_today', 0),
                    'max_submissions_per_day': data.get('maxDailySubmissions', 7),
                    'leaderboard_position': data.get('userRank', None)
                }
            else:
                self.logger.warning(f"⚠️ No se pudo obtener info de competencia: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo info de competencia: {e}")
            return None
    
    def subir_submission(self, archivo_csv, mensaje="Submission automática"):
        """Subir submission a la competencia"""
        
        self.logger.info(f"📤 Intentando subir submission: {archivo_csv}")
        
        if not os.path.exists(archivo_csv):
            self.logger.error(f"❌ Archivo no encontrado: {archivo_csv}")
            return False, "Archivo no encontrado"
        
        try:
            # Verificar límite de submissions diarias
            info_comp = self.obtener_info_competencia()
            if info_comp and info_comp['submissions_today'] >= Config.MAX_SUBMISSIONS_PER_DAY:
                mensaje_error = f"❌ Límite diario alcanzado: {info_comp['submissions_today']}/{Config.MAX_SUBMISSIONS_PER_DAY}"
                self.logger.warning(mensaje_error)
                return False, mensaje_error
            
            # Preparar archivos para upload
            files = {
                'file': open(archivo_csv, 'rb')
            }
            
            data = {
                'competitionId': 'neuro-kup-ii-beta-acm-ai',
                'submissionDescription': mensaje
            }
            
            # Endpoint de submission (ajustar según API real)
            url = f"{Config.API_BASE_URL}/competitions/submissions/submit"
            response = self.session.post(url, files=files, data=data)
            
            files['file'].close()
            
            if response.status_code == 200:
                result = response.json()
                submission_id = result.get('submissionId', 'unknown')
                
                self.logger.info(f"✅ Submission exitosa: ID {submission_id}")
                return True, submission_id
            else:
                error_msg = f"❌ Error en submission: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"❌ Excepción en submission: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def obtener_resultados_submission(self, submission_id):
        """Obtener resultados de una submission"""
        
        try:
            url = f"{Config.API_BASE_URL}/competitions/submissions/{submission_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'id': submission_id,
                    'status': data.get('status'),
                    'public_score': data.get('publicScore'),
                    'private_score': data.get('privateScore'),
                    'date': data.get('date'),
                    'leaderboard_position': data.get('publicLeaderboardPosition')
                }
            else:
                self.logger.warning(f"⚠️ No se pudieron obtener resultados: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo resultados: {e}")
            return None

class DatabaseManager:
    """Gestor de base de datos para submissions"""
    
    def __init__(self, db_file=Config.DB_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos"""
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Tabla de submissions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                archivo_csv TEXT,
                f1_score_local REAL,
                f1_score_publico REAL,
                f1_score_privado REAL,
                posicion_leaderboard INTEGER,
                mensaje TEXT,
                hash_archivo TEXT,
                status TEXT DEFAULT 'pending',
                modelo_usado TEXT,
                parametros_modelo TEXT
            )
        ''')
        
        # Tabla de entrenamientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entrenamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                f1_score REAL,
                archivo_modelo TEXT,
                estrategia_usada TEXT,
                tiempo_entrenamiento REAL,
                mejora_sobre_anterior REAL,
                parametros TEXT
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def registrar_submission(self, submission_data):
        """Registrar nueva submission"""
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions (
                submission_id, archivo_csv, f1_score_local, mensaje, 
                hash_archivo, modelo_usado, parametros_modelo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            submission_data.get('submission_id'),
            submission_data.get('archivo_csv'),
            submission_data.get('f1_score_local'),
            submission_data.get('mensaje'),
            submission_data.get('hash_archivo'),
            submission_data.get('modelo_usado'),
            submission_data.get('parametros_modelo')
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"📝 Submission registrada en DB: {submission_data.get('submission_id')}")
    
    def actualizar_resultados_submission(self, submission_id, resultados):
        """Actualizar resultados de submission"""
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE submissions SET
                f1_score_publico = ?,
                f1_score_privado = ?,
                posicion_leaderboard = ?,
                status = ?
            WHERE submission_id = ?
        ''', (
            resultados.get('public_score'),
            resultados.get('private_score'),
            resultados.get('leaderboard_position'),
            resultados.get('status'),
            submission_id
        ))
        
        conn.commit()
        conn.close()
    
    def obtener_mejor_submission(self):
        """Obtener la mejor submission hasta ahora"""
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM submissions 
            WHERE f1_score_publico IS NOT NULL 
            ORDER BY f1_score_publico DESC 
            LIMIT 1
        ''')
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado
    
    def registrar_entrenamiento(self, entrenamiento_data):
        """Registrar nuevo entrenamiento"""
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO entrenamientos (
                f1_score, archivo_modelo, estrategia_usada, 
                tiempo_entrenamiento, mejora_sobre_anterior, parametros
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            entrenamiento_data.get('f1_score'),
            entrenamiento_data.get('archivo_modelo'),
            entrenamiento_data.get('estrategia_usada'),
            entrenamiento_data.get('tiempo_entrenamiento'),
            entrenamiento_data.get('mejora_sobre_anterior'),
            entrenamiento_data.get('parametros')
        ))
        
        conn.commit()
        conn.close()
    
    def obtener_estadisticas(self):
        """Obtener estadísticas generales"""
        
        conn = sqlite3.connect(self.db_file)
        
        # Submissions
        df_submissions = pd.read_sql_query(
            "SELECT * FROM submissions ORDER BY timestamp DESC", 
            conn
        )
        
        # Entrenamientos
        df_entrenamientos = pd.read_sql_query(
            "SELECT * FROM entrenamientos ORDER BY timestamp DESC LIMIT 10", 
            conn
        )
        
        conn.close()
        
        return {
            'submissions': df_submissions,
            'entrenamientos': df_entrenamientos,
            'total_submissions': len(df_submissions),
            'mejor_score_publico': df_submissions['f1_score_publico'].max() if len(df_submissions) > 0 else None,
            'submissions_hoy': len(df_submissions[df_submissions['timestamp'].str.startswith(datetime.now().strftime('%Y-%m-%d'))])
        }

class AutoTrainingSystem:
    """Sistema de entrenamiento automático y submissions"""
    
    def __init__(self, username, api_key):
        self.api = NeuroKupAPI(username, api_key)
        self.db = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # Estado del sistema
        self.mejor_score_local = 0
        self.ultimo_entrenamiento = None
        self.submissions_hoy = 0
    
    def calcular_hash_archivo(self, archivo):
        """Calcular hash MD5 de archivo"""
        
        hash_md5 = hashlib.md5()
        with open(archivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def entrenar_nuevo_modelo(self):
        """Entrenar nuevo modelo con mejoras"""
        
        self.logger.info("🤖 Iniciando entrenamiento de nuevo modelo")
        
        try:
            inicio = datetime.now()
            
            # Usar sistema de mejora iterativa
            mejor_modelo, score, historial = mejorar_modelo_automatico(
                'train_local.csv',  # Ajustar según archivo disponible
                score_base=self.mejor_score_local
            )
            
            tiempo_entrenamiento = (datetime.now() - inicio).total_seconds()
            
            # Guardar modelo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_modelo = f"{Config.MODELS_DIR}/modelo_{timestamp}.pkl"
            
            with open(archivo_modelo, 'wb') as f:
                pickle.dump(mejor_modelo, f)
            
            # Registrar entrenamiento
            mejora = score - self.mejor_score_local
            
            entrenamiento_data = {
                'f1_score': score,
                'archivo_modelo': archivo_modelo,
                'estrategia_usada': 'mejora_iterativa_automatica',
                'tiempo_entrenamiento': tiempo_entrenamiento,
                'mejora_sobre_anterior': mejora,
                'parametros': json.dumps(historial[-1] if historial else {})
            }
            
            self.db.registrar_entrenamiento(entrenamiento_data)
            
            # Actualizar mejor score si hay mejora
            if score > self.mejor_score_local:
                self.logger.info(f"🎉 Mejora encontrada: {score:.4f} (+{mejora:.4f})")
                self.mejor_score_local = score
                self.ultimo_entrenamiento = archivo_modelo
                return True, score, archivo_modelo
            else:
                self.logger.info(f"❌ Sin mejora: {score:.4f} (actual: {self.mejor_score_local:.4f})")
                return False, score, archivo_modelo
                
        except Exception as e:
            self.logger.error(f"❌ Error en entrenamiento: {e}")
            return False, 0, None
    
    def generar_submission(self, modelo_archivo):
        """Generar archivo de submission"""
        
        self.logger.info(f"📝 Generando submission con modelo: {modelo_archivo}")
        
        try:
            # Cargar modelo
            with open(modelo_archivo, 'rb') as f:
                modelo = pickle.load(f)
            
            # Hacer predicciones
            pred_public, f1_public = calcularf1_score.obtenerscore('test_public.csv', modelo)
            pred_private, _ = calcularf1_score.obtenerscore('test_private.csv', modelo)            # Crear submission
            submission = calcularf1_score.crear_submission_final(
                pred_public, pred_private, 
                filename="solucion.csv"
            )
            
            archivo_submission = "solucion.csv"
            submission.to_csv(archivo_submission, index=False)
            
            return archivo_submission, f1_public
            
        except Exception as e:
            self.logger.error(f"❌ Error generando submission: {e}")
            return None, None
    
    def evaluar_y_subir_si_mejora(self):
        """Evaluar modelo y subir si hay mejora"""
        
        self.logger.info("🔍 Evaluando si subir nueva submission")
        
        # Verificar límite diario
        stats = self.db.obtener_estadisticas()
        if stats['submissions_hoy'] >= Config.MAX_SUBMISSIONS_PER_DAY:
            self.logger.warning(f"⚠️ Límite diario alcanzado: {stats['submissions_hoy']}/{Config.MAX_SUBMISSIONS_PER_DAY}")
            return False
        
        # Entrenar nuevo modelo
        hay_mejora, score, modelo_archivo = self.entrenar_nuevo_modelo()
        
        if not hay_mejora:
            self.logger.info("❌ Sin mejora suficiente, no se sube submission")
            return False
        
        # Verificar mejora mínima
        mejor_anterior = self.db.obtener_mejor_submission()
        if mejor_anterior:
            score_anterior = mejor_anterior[5]  # f1_score_publico
            if score_anterior and (score - score_anterior) < Config.MIN_MEJORA_REQUERIDA:
                self.logger.info(f"❌ Mejora insuficiente: {score:.4f} vs {score_anterior:.4f}")
                return False
        
        # Generar submission
        archivo_submission, f1_local = self.generar_submission(modelo_archivo)
        
        if not archivo_submission:
            self.logger.error("❌ Error generando submission")
            return False
        
        # Subir submission
        exito, resultado = self.api.subir_submission(
            archivo_submission, 
            f"Auto-submission F1:{score:.4f} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        )
        
        if exito:
            # Registrar en base de datos
            submission_data = {
                'submission_id': resultado,
                'archivo_csv': archivo_submission,
                'f1_score_local': f1_local,
                'mensaje': f"Auto-submission F1:{score:.4f}",
                'hash_archivo': self.calcular_hash_archivo(archivo_submission),
                'modelo_usado': modelo_archivo,
                'parametros_modelo': json.dumps({'score': score})
            }
            
            self.db.registrar_submission(submission_data)
            
            self.logger.info(f"✅ Submission exitosa: {resultado}")
            return True
        else:
            self.logger.error(f"❌ Error en submission: {resultado}")
            return False
    
    def verificar_resultados_pendientes(self):
        """Verificar resultados de submissions pendientes"""
        
        conn = sqlite3.connect(Config.DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT submission_id FROM submissions WHERE status = 'pending'")
        pendientes = cursor.fetchall()
        conn.close()
        
        for (submission_id,) in pendientes:
            resultados = self.api.obtener_resultados_submission(submission_id)
            if resultados and resultados['status'] == 'complete':
                self.db.actualizar_resultados_submission(submission_id, resultados)
                self.logger.info(f"📊 Resultados actualizados: {submission_id} - Score: {resultados.get('public_score')}")
    
    def ejecutar_ciclo_completo(self):
        """Ejecutar un ciclo completo de entrenamiento y evaluación"""
        
        self.logger.info("🔄 Iniciando ciclo completo")
        
        try:
            # 1. Verificar conexión
            if not self.api.verificar_conexion():
                self.logger.error("❌ Sin conexión con API")
                return
            
            # 2. Actualizar resultados pendientes
            self.verificar_resultados_pendientes()
            
            # 3. Evaluar y subir si hay mejora
            self.evaluar_y_subir_si_mejora()
            
            # 4. Mostrar estadísticas
            stats = self.db.obtener_estadisticas()
            self.logger.info(f"📊 Stats: {stats['total_submissions']} submissions, mejor: {stats['mejor_score_publico']}")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo completo: {e}")
    
    def iniciar_sistema_automatico(self):
        """Iniciar sistema automático con scheduler"""
        
        self.logger.info("🚀 Iniciando sistema automático")
        
        # Programar tareas
        schedule.every(Config.ENTRENAMIENTO_INTERVALO_HORAS).hours.do(self.ejecutar_ciclo_completo)
        schedule.every(Config.VERIFICACION_INTERVALO_MINUTOS).minutes.do(self.verificar_resultados_pendientes)
        
        self.running = True
        
        # Ejecutar inmediatamente
        self.ejecutar_ciclo_completo()
        
        # Loop principal
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    
    def detener_sistema(self):
        """Detener sistema automático"""
        
        self.running = False
        self.logger.info("🛑 Sistema automático detenido")
    
    def generar_reporte(self):
        """Generar reporte de actividad"""
        
        stats = self.db.obtener_estadisticas()
        
        reporte = f"""
📊 REPORTE DEL SISTEMA AUTOMÁTICO
================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUBMISSIONS:
- Total: {stats['total_submissions']}
- Hoy: {stats['submissions_hoy']}
- Mejor score público: {stats['mejor_score_publico']}

ENTRENAMIENTOS RECIENTES:
"""
        
        for _, row in stats['entrenamientos'].head(5).iterrows():
            reporte += f"- {row['timestamp']}: F1={row['f1_score']:.4f} (+{row['mejora_sobre_anterior']:.4f})\n"
        
        return reporte

# ================================
# 🎮 FUNCIONES PRINCIPALES
# ================================

def configurar_credenciales(username, api_key):
    """Configurar credenciales de Kaggle"""
    
    credenciales = {
        'username': username,
        'key': api_key,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(Config.CREDENTIALS_FILE, 'w') as f:
        json.dump(credenciales, f, indent=2)
    
    print(f"✅ Credenciales guardadas en {Config.CREDENTIALS_FILE}")

def cargar_credenciales():
    """Cargar credenciales de archivo"""
    
    if not os.path.exists(Config.CREDENTIALS_FILE):
        raise FileNotFoundError(f"❌ No se encontró {Config.CREDENTIALS_FILE}")
    
    with open(Config.CREDENTIALS_FILE, 'r') as f:
        credenciales = json.load(f)
    
    return credenciales['username'], credenciales['key']

def iniciar_sistema_automatico():
    """Iniciar sistema completo automático"""
    
    print("🚀 INICIANDO SISTEMA AUTOMÁTICO DE SUBMISSIONS")
    print("="*60)
    
    try:
        # Cargar credenciales
        username, api_key = cargar_credenciales()
        print(f"✅ Credenciales cargadas para: {username}")
        
        # Crear sistema
        sistema = AutoTrainingSystem(username, api_key)
        
        # Iniciar
        sistema.iniciar_sistema_automatico()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por usuario")
    except Exception as e:
        print(f"❌ Error iniciando sistema: {e}")

def enviar_submission_manual(archivo_csv, mensaje="Submission manual"):
    """Enviar submission manualmente"""
    
    try:
        username, api_key = cargar_credenciales()
        api = NeuroKupAPI(username, api_key)
        
        exito, resultado = api.subir_submission(archivo_csv, mensaje)
        
        if exito:
            print(f"✅ Submission exitosa: {resultado}")
            
            # Registrar en DB
            db = DatabaseManager()
            submission_data = {
                'submission_id': resultado,
                'archivo_csv': archivo_csv,
                'mensaje': mensaje,
                'hash_archivo': hashlib.md5(open(archivo_csv, 'rb').read()).hexdigest(),
            }
            db.registrar_submission(submission_data)
            
        else:
            print(f"❌ Error en submission: {resultado}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

# ================================
# 📋 EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    print("🤖 API DE SUBMISSION AUTOMÁTICA - NEUROKUP II")
    print("="*60)
    print("📝 Configuración inicial:")
    print("  1. configurar_credenciales('tu_username', 'tu_api_key')")
    print("  2. iniciar_sistema_automatico()")
    print()
    print("📝 Uso manual:")
    print("  • enviar_submission_manual('submission.csv', 'Mi mensaje')")
    print()
    print("🔧 Funciones disponibles:")
    print("  • configurar_credenciales(username, api_key)")
    print("  • iniciar_sistema_automatico()")
    print("  • enviar_submission_manual(archivo, mensaje)")
    print("="*60)
    
    # Ejemplo de configuración
    respuesta = input("\n¿Configurar credenciales ahora? (s/n): ").lower().strip()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        username = input("Username de Kaggle: ")
        api_key = input("API Key de Kaggle: ")
        configurar_credenciales(username, api_key)
        
        iniciar_ahora = input("\n¿Iniciar sistema automático? (s/n): ").lower().strip()
        if iniciar_ahora in ['s', 'si', 'sí', 'y', 'yes']:
            iniciar_sistema_automatico()