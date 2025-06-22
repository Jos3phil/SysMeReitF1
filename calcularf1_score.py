# ================================
# 📊 calcularf1_score.py - MÓDULO PARA PREDICCIONES FINALES
# ================================
# Sistema modular para manejar test_public y test_private

import pandas as pd
import numpy as np
import os
from datetime import datetime

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report, confusion_matrix
import warnings
from datetime import datetime
import os
warnings.filterwarnings('ignore')

# Variables globales
CALCULAR_F1 = True
MODELO_GLOBAL = None

class ModeloCoronario:
    """
    Clase para manejar el modelo de predicción de enfermedad coronaria
    """
    
    def __init__(self):
        self.modelo_entrenado = None
        self.encoders = {}
        self.feature_columns = None
        self.threshold_optimo = 0.5
        self.modelo_ensemble = None
        
    def limpiar_datos(self, df):
        """Limpieza y estandarización de datos"""
        
        df_clean = df.copy()
        
        # Convertir todas las columnas a tipos básicos
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object' or str(df_clean[col].dtype) == 'category':
                df_clean[col] = df_clean[col].astype(str)
        
        # Estandarización de valores binarios (como hicimos antes)
        columnas_binarias = [
            'Actividades físicas', 'Presión arterial alta', 'Colesterol alto',
            'Cáncer de piel', 'Cáncer', 'Bronquitis', 'Depresión', 
            'Enfermedad renal', 'Diabetes', 'Artritis', 'Dificultad al caminar',
            'Fumar', 'Productos de tabaco', 'Bebebidas alcoholicas', 'VIH', 
            'Frutas', 'Vegetales'
        ]
        
        # Mapeos de limpieza
        mapeo_si = ['si', 'sí', 'Si', 'Sí', 'SI', 'SÍ', 'yes', 'Yes', 'YES', 'y', 'Y', 'true', 'True', '1']
        mapeo_no = ['no', 'No', 'NO', 'n', 'N', 'false', 'False', '0']
        
        for col in columnas_binarias:
            if col in df_clean.columns:
                # Estandarizar valores
                df_clean[col] = df_clean[col].replace(mapeo_si, 'Sí')
                df_clean[col] = df_clean[col].replace(mapeo_no, 'No')
                df_clean[col] = df_clean[col].replace(['nan', 'None', 'NaN'], np.nan)
        
        return df_clean
    
    def imputar_nulos(self, df):
        """Imputación inteligente de valores nulos"""
        
        df_imputed = df.copy()
        
        # Imputación conservadora para variables de hábitos
        habitos_conservadores = {
            'Frutas': 'No',
            'Vegetales': 'No', 
            'Actividades físicas': 'No',
            'Fumar': 'No',
            'Productos de tabaco': 'No',
            'Bebebidas alcoholicas': 'No'
        }
        
        # Imputación médica para condiciones
        condiciones_medicas = [
            'Colesterol alto', 'VIH', 'Presión arterial alta',
            'Diabetes', 'Cáncer', 'Depresión', 'Artritis'
        ]
        
        # Aplicar imputación conservadora
        for col, valor_default in habitos_conservadores.items():
            if col in df_imputed.columns:
                df_imputed[col].fillna(valor_default, inplace=True)
        
        # Aplicar moda para condiciones médicas
        for col in condiciones_medicas:
            if col in df_imputed.columns:
                moda = df_imputed[col].mode()
                if len(moda) > 0:
                    df_imputed[col].fillna(moda.iloc[0], inplace=True)
                else:
                    df_imputed[col].fillna('No', inplace=True)
        
        # Para otras columnas categóricas, usar moda
        for col in df_imputed.select_dtypes(include=['object']).columns:
            if col != 'ID' and col != 'Condición':
                moda = df_imputed[col].mode()
                if len(moda) > 0:
                    df_imputed[col].fillna(moda.iloc[0], inplace=True)
        
        # Para columnas numéricas, usar mediana
        for col in df_imputed.select_dtypes(include=[np.number]).columns:
            if col != 'ID' and col != 'Condición':
                mediana = df_imputed[col].median()
                df_imputed[col].fillna(mediana, inplace=True)
        
        return df_imputed
    
    def feature_engineering(self, df):
        """Feature engineering avanzado"""
        
        df_features = df.copy()
        
        # 1. Score de riesgo cardiovascular
        condiciones_riesgo = ['Diabetes', 'Presión arterial alta', 'Colesterol alto', 'Fumar']
        df_features['Score_Riesgo_Cardiovascular'] = 0
        
        for cond in condiciones_riesgo:
            if cond in df_features.columns:
                df_features['Score_Riesgo_Cardiovascular'] += (df_features[cond] == 'Sí').astype(int)
        
        # 2. Score de enfermedades crónicas
        condiciones_cronicas = ['Cáncer', 'Artritis', 'Depresión', 'Enfermedad renal']
        df_features['Score_Enfermedades_Cronicas'] = 0
        
        for cond in condiciones_cronicas:
            if cond in df_features.columns:
                df_features['Score_Enfermedades_Cronicas'] += (df_features[cond] == 'Sí').astype(int)
        
        # 3. Score de hábitos saludables
        habitos_saludables = ['Actividades físicas', 'Frutas', 'Vegetales']
        df_features['Score_Habitos_Saludables'] = 0
        
        for habito in habitos_saludables:
            if habito in df_features.columns:
                df_features['Score_Habitos_Saludables'] += (df_features[habito] == 'Sí').astype(int)
        
        # 4. Categorías de edad
        if 'Edad' in df_features.columns:
            df_features['Es_Mayor_65'] = (df_features['Edad'] >= 65).astype(int)
            df_features['Es_Adulto_Mayor'] = (df_features['Edad'] >= 55).astype(int)
        
        # 5. Interacciones importantes
        if 'Edad' in df_features.columns and 'Diabetes' in df_features.columns:
            df_features['Edad_x_Diabetes'] = df_features['Edad'] * (df_features['Diabetes'] == 'Sí').astype(int)
        
        return df_features
    
    def preparar_para_ml(self, df, es_entrenamiento=True):
        """Preparar datos para machine learning"""
        
        df_ml = df.copy()
        
        # Identificar columnas a excluir
        excluir = ['ID']
        if 'Condición' in df_ml.columns and not es_entrenamiento:
            excluir.append('Condición')
        
        # Separar features
        if es_entrenamiento and 'Condición' in df_ml.columns:
            y = df_ml['Condición']
            X = df_ml.drop(excluir + ['Condición'], axis=1)
        else:
            y = None
            X = df_ml.drop(excluir, axis=1, errors='ignore')
        
        # Guardar columnas para consistencia
        if es_entrenamiento:
            self.feature_columns = X.columns.tolist()
        else:
            # Asegurar mismas columnas que en entrenamiento
            if self.feature_columns is not None:
                # Agregar columnas faltantes con valor por defecto
                for col in self.feature_columns:
                    if col not in X.columns:
                        X[col] = 0  # Valor por defecto
                
                # Reordenar columnas
                X = X[self.feature_columns]
        
        # Encoding categórico
        X_encoded = pd.DataFrame(index=X.index)
        
        for col in X.columns:
            if X[col].dtype in ['int64', 'float64']:
                # Variables numéricas
                X_encoded[col] = X[col].values
            else:
                # Variables categóricas
                valores_limpios = X[col].fillna('MISSING').astype(str)
                
                if es_entrenamiento:
                    # Crear encoder
                    le = LabelEncoder()
                    X_encoded[col] = le.fit_transform(valores_limpios)
                    self.encoders[col] = le
                else:
                    # Usar encoder existente
                    if col in self.encoders:
                        le = self.encoders[col]
                        try:
                            # Manejar valores no vistos
                            valores_encoded = []
                            for valor in valores_limpios:
                                if valor in le.classes_:
                                    valores_encoded.append(le.transform([valor])[0])
                                else:
                                    # Valor no visto, usar el más frecuente (0)
                                    valores_encoded.append(0)
                            X_encoded[col] = valores_encoded
                        except:
                            X_encoded[col] = 0
                    else:
                        X_encoded[col] = 0
        
        return X_encoded, y
    
    def entrenar_modelo(self, df_train):
        """Entrenar el modelo completo"""
        
        print("🚀 ENTRENANDO MODELO COMPLETO")
        print("="*40)
        
        # 1. Limpiar datos
        df_clean = self.limpiar_datos(df_train)
        
        # 2. Imputar nulos
        df_imputed = self.imputar_nulos(df_clean)
        
        # 3. Feature engineering
        df_features = self.feature_engineering(df_imputed)
        
        # 4. Preparar para ML
        X, y = self.preparar_para_ml(df_features, es_entrenamiento=True)
        
        print(f"📊 Dataset preparado: {X.shape}")
        print(f"🎯 Target balance: {y.value_counts().to_dict()}")
        
        # 5. Entrenar modelo base
        modelo_base = RandomForestClassifier(
            n_estimators=200,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        modelo_base.fit(X, y)
        
        # 6. Optimizar threshold
        y_proba = modelo_base.predict_proba(X)[:, 1]
        thresholds = np.arange(0.1, 0.9, 0.05)
        best_f1 = 0
        
        for thresh in thresholds:
            y_pred_thresh = (y_proba >= thresh).astype(int)
            f1_thresh = f1_score(y, y_pred_thresh)
            if f1_thresh > best_f1:
                best_f1 = f1_thresh
                self.threshold_optimo = thresh
        
        # 7. Crear ensemble
        rf_model = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        self.modelo_ensemble = VotingClassifier(
            estimators=[('rf', rf_model), ('gb', gb_model)],
            voting='soft'
        )
        
        self.modelo_ensemble.fit(X, y)
        
        # 8. Seleccionar mejor modelo (ensemble vs base con threshold)
        y_pred_ensemble = self.modelo_ensemble.predict(X)
        y_pred_threshold = (modelo_base.predict_proba(X)[:, 1] >= self.threshold_optimo).astype(int)
        
        f1_ensemble = f1_score(y, y_pred_ensemble)
        f1_threshold = f1_score(y, y_pred_threshold)
        
        if f1_ensemble > f1_threshold:
            self.modelo_entrenado = self.modelo_ensemble
            print(f"✅ Usando Ensemble - F1: {f1_ensemble:.4f}")
        else:
            self.modelo_entrenado = modelo_base
            print(f"✅ Usando RF con threshold - F1: {f1_threshold:.4f}")
        
        print(f"🎚️ Threshold óptimo: {self.threshold_optimo:.3f}")
        
        return max(f1_ensemble, f1_threshold)
    
    def predecir(self, df_test, calcular_f1=False):
        """Hacer predicciones en dataset de test"""
        
        if self.modelo_entrenado is None:
            raise ValueError("❌ Modelo no entrenado. Ejecuta entrenar_modelo() primero.")
        
        print("🔮 HACIENDO PREDICCIONES")
        print("="*30)
        
        # 1. Procesar datos igual que en entrenamiento
        df_clean = self.limpiar_datos(df_test)
        df_imputed = self.imputar_nulos(df_clean)
        df_features = self.feature_engineering(df_imputed)
        
        # 2. Preparar para ML
        X_test, y_test = self.preparar_para_ml(df_features, es_entrenamiento=False)
        
        print(f"📊 Test preparado: {X_test.shape}")
        
        # 3. Hacer predicciones
        if self.modelo_entrenado == self.modelo_ensemble:
            # Usar ensemble
            y_pred = self.modelo_entrenado.predict(X_test)
            y_proba = self.modelo_entrenado.predict_proba(X_test)[:, 1]
        else:
            # Usar modelo base con threshold
            y_proba = self.modelo_entrenado.predict_proba(X_test)[:, 1]
            y_pred = (y_proba >= self.threshold_optimo).astype(int)
        
        # 4. Crear DataFrame de resultados
        resultados = pd.DataFrame({
            'ID': df_test['ID'],
            'Condición': y_pred,
            'Probabilidad': y_proba
        })
        
        # 5. Calcular F1 si se puede
        f1_resultado = None
        if calcular_f1 and y_test is not None:
            f1_resultado = f1_score(y_test, y_pred)
            print(f"🎯 F1-Score: {f1_resultado:.4f}")
            
            # Reporte detallado
            print("\n📋 Classification Report:")
            print(classification_report(y_test, y_pred))
        
        print(f"✅ Predicciones completadas: {len(resultados)} casos")
        
        return resultados, f1_resultado

# ================================
# 🎮 FUNCIONES PRINCIPALES PARA IMPORTAR
# ================================

def entrenar_y_evaluar(df_train):
    """
    Función principal para entrenar modelo y obtener F1-score
    
    Args:
        df_train: DataFrame con datos de entrenamiento (debe tener columna 'Condición')
    
    Returns:
        tuple: (modelo_entrenado, f1_score)
    """
    
    modelo = ModeloCoronario()
    f1_score_entrenamiento = modelo.entrenar_modelo(df_train)
    
    return modelo, f1_score_entrenamiento

def obtenerscore(df_test, modelo_entrenado=None):
    """
    Función principal para obtener predicciones y F1-score si es posible
    
    Args:
        df_test: DataFrame de test (puede tener o no 'Condición')
        modelo_entrenado: Modelo ya entrenado (opcional)
    
    Returns:
        tuple: (predicciones_df, f1_score_o_none)
    """
    
    if modelo_entrenado is None:
        raise ValueError("❌ Necesitas un modelo entrenado. Usa entrenar_y_evaluar() primero.")
    
    # Detectar si tiene columna target
    tiene_target = 'Condición' in df_test.columns
    
    print(f"🔍 Dataset detectado: {'CON target (test_public)' if tiene_target else 'SIN target (test_private)'}")
    
    # Hacer predicciones
    predicciones, f1_score = modelo_entrenado.predecir(df_test, calcular_f1=tiene_target)
    
    return predicciones, f1_score

def crear_submission_final(predicciones_public, predicciones_private, filename='solucion.csv'):
    """
    Crear archivo de submission final combinando ambos datasets
    
    Args:
        predicciones_public: DataFrame con predicciones de test_public
        predicciones_private: DataFrame con predicciones de test_private
        filename: Nombre del archivo de salida
    
    Returns:
        DataFrame: Submission final
    """
    
    print("📝 CREANDO SUBMISSION FINAL")
    print("="*30)
    
    # Combinar predicciones
    submission = pd.concat([
        predicciones_public[['ID', 'Condición']], 
        predicciones_private[['ID', 'Condición']]
    ], ignore_index=True)
    
    # Verificar formato
    print(f"📊 Total predicciones: {len(submission):,}")
    print(f"📊 IDs únicos: {submission['ID'].nunique():,}")
    print(f"📊 Distribución predicciones: {submission['Condición'].value_counts().to_dict()}")
    
    # Guardar archivo
    submission.to_csv(filename, index=False)
    print(f"💾 Archivo guardado: {filename}")
    
    return submission

# ================================
# 🚀 FUNCIONES PRINCIPALES SIMPLIFICADAS
# ================================

def obtener_score(archivo_csv, modelo=None, tiene_target=None):
    """
    Función principal para obtener F1-Score de un dataset
    
    Args:
        archivo_csv (str): Ruta al archivo CSV ('test_public.csv' o 'test_private.csv')
        modelo (ModeloCoronario): Modelo entrenado (opcional, se entrena automáticamente)
        tiene_target (bool): Si None, se detecta automáticamente
    
    Returns:
        tuple: (predicciones_df, f1_score o None)
    """
    
    print(f"🎯 ANALIZANDO: {archivo_csv}")
    print("="*50)
    
    # Cargar datos
    if not os.path.exists(archivo_csv):
        raise FileNotFoundError(f"❌ No se encuentra el archivo: {archivo_csv}")
    
    df = pd.read_csv(archivo_csv)
    print(f"📊 Datos cargados: {df.shape[0]:,} filas × {df.shape[1]} columnas")
    
    # Detectar si tiene target automáticamente
    if tiene_target is None:
        tiene_target = 'Condición' in df.columns
        print(f"🎯 Target detectado: {'Sí' if tiene_target else 'No'}")
    
    # Entrenar modelo si no se proporciona
    if modelo is None:
        print("🤖 Entrenando modelo automáticamente...")
        modelo = entrenar_modelo_completo()
    
    # Hacer predicciones
    predicciones, f1_resultado = modelo.predecir(df, calcular_f1=tiene_target)
    
    print(f"✅ Predicciones completadas para {archivo_csv}")
    if f1_resultado is not None:
        print(f"🏆 F1-Score: {f1_resultado:.4f}")
    
    return predicciones, f1_resultado

def entrenar_modelo_completo(usar_archivo='train.csv'):
    """
    Entrena un modelo completo usando el dataset especificado
    
    Args:
        usar_archivo (str): Archivo de entrenamiento a usar
    
    Returns:
        ModeloCoronario: Modelo entrenado
    """
    
    print(f"🚀 ENTRENANDO MODELO CON: {usar_archivo}")
    print("="*50)
    
    # Cargar datos de entrenamiento
    if not os.path.exists(usar_archivo):
        # Intentar archivos alternativos
        archivos_alt = ['train_local.csv', 'train_colab.csv', 'train.csv']
        for archivo in archivos_alt:
            if os.path.exists(archivo):
                usar_archivo = archivo
                print(f"📁 Usando archivo alternativo: {archivo}")
                break
        else:
            raise FileNotFoundError("❌ No se encuentra ningún archivo de entrenamiento")
    
    df_train = pd.read_csv(usar_archivo)
    print(f"📊 Dataset entrenamiento: {df_train.shape[0]:,} filas × {df_train.shape[1]} columnas")
    
    # Crear y entrenar modelo
    modelo = ModeloCoronario()
    f1_entrenamiento = modelo.entrenar_modelo(df_train)
    
    print(f"✅ Modelo entrenado - F1: {f1_entrenamiento:.4f}")
    
    # Guardar modelo globalmente para reutilización
    global MODELO_GLOBAL
    MODELO_GLOBAL = modelo
    
    return modelo

def generar_predicciones(archivo_test, archivo_salida, modelo=None):
    """
    Genera archivo de predicciones para submission
    
    Args:
        archivo_test (str): Archivo de test ('test_private.csv' o 'test_public.csv')
        archivo_salida (str): Nombre del archivo de salida
        modelo (ModeloCoronario): Modelo entrenado (opcional)
    
    Returns:
        pd.DataFrame: DataFrame con predicciones
    """
    
    print(f"📝 GENERANDO PREDICCIONES: {archivo_test} → {archivo_salida}")
    print("="*60)
    
    # Obtener predicciones
    predicciones, f1_score = obtener_score(archivo_test, modelo, tiene_target=False)
    
    # Formato para submission (solo ID y Condición)
    submission = predicciones[['ID', 'Condición']].copy()
    
    # Guardar archivo
    submission.to_csv(archivo_salida, index=False)
    print(f"💾 Archivo guardado: {archivo_salida}")
    print(f"📊 Predicciones: {len(submission):,}")
    print(f"📊 Distribución: {submission['Condición'].value_counts().to_dict()}")
    
    return submission

def procesar_ambos_datasets(modelo=None):
    """
    Procesa tanto test_public.csv como test_private.csv
    
    Args:
        modelo (ModeloCoronario): Modelo entrenado (opcional)
    
    Returns:
        dict: Resultados de ambos datasets
    """
    
    print("🎯 PROCESANDO AMBOS DATASETS DE TEST")
    print("="*50)
    
    resultados = {}
    
    # Entrenar modelo si no se proporciona
    if modelo is None:
        modelo = entrenar_modelo_completo()
    
    # Procesar test_public.csv (tiene target)
    if os.path.exists('test_public.csv'):
        print("\n📊 PROCESANDO TEST_PUBLIC.CSV:")
        pred_public, f1_public = obtener_score('test_public.csv', modelo, tiene_target=True)
        resultados['public'] = {
            'predicciones': pred_public,
            'f1_score': f1_public,
            'archivo': 'test_public.csv'
        }
        
        # Guardar predicciones
        generar_predicciones('test_public.csv', 'predicciones_public.csv', modelo)
    else:
        print("⚠️ test_public.csv no encontrado")
    
    # Procesar test_private.csv (sin target)
    if os.path.exists('test_private.csv'):
        print("\n📊 PROCESANDO TEST_PRIVATE.CSV:")
        pred_private, _ = obtener_score('test_private.csv', modelo, tiene_target=False)
        resultados['private'] = {
            'predicciones': pred_private,
            'f1_score': None,
            'archivo': 'test_private.csv'
        }
          # Guardar predicciones
        generar_predicciones('test_private.csv', 'predicciones_private.csv', modelo)
    else:
        print("⚠️ test_private.csv no encontrado")
      # Crear submission combinada si ambos existen
    if 'public' in resultados and 'private' in resultados:
        print("\n📝 CREANDO SUBMISSION COMBINADA:")
        submission_combinada = pd.concat([
            resultados['public']['predicciones'][['ID', 'Condición']],
            resultados['private']['predicciones'][['ID', 'Condición']]
        ], ignore_index=True)
        
        archivo_final = 'solucion.csv'
        submission_combinada.to_csv(archivo_final, index=False)
        print(f"💾 Submission final: {archivo_final}")
        
        resultados['submission_final'] = {
            'archivo': archivo_final,
            'total_predicciones': len(submission_combinada)
        }
    
    return resultados

def calcular_f1_ponderado_datasets():
    """
    Calcula F1-Score ponderado entre train_local.csv y train_colab.csv
    (Requiere que ambos archivos existan y se entrenen por separado)
    """
    
    print("🎯 CALCULANDO F1-SCORE PONDERADO")
    print("="*50)
    
    resultados_f1 = {}
    
    # Entrenar con train_local.csv
    if os.path.exists('train_local.csv'):
        print("\n🏠 ENTRENANDO CON TRAIN_LOCAL.CSV:")
        modelo_local = entrenar_modelo_completo('train.csv')

        
        # Evaluar en test_public si existe
        if os.path.exists('test_public.csv'):
            _, f1_local = obtener_score('test_public.csv', modelo_local, tiene_target=True)
            resultados_f1['local'] = f1_local
        
    # Entrenar con train_colab.csv  
    if os.path.exists('train_colab.csv'):
        print("\n☁️ ENTRENANDO CON TRAIN_COLAB.CSV:")
        modelo_colab = entrenar_modelo_completo('train_colab.csv')
        
        # Evaluar en test_public si existe
        if os.path.exists('test_public.csv'):
            _, f1_colab = obtener_score('test_public.csv', modelo_colab, tiene_target=True)
            resultados_f1['colab'] = f1_colab
    
    # Calcular F1 ponderado
    if 'local' in resultados_f1 and 'colab' in resultados_f1:
        # Pesos basados en tamaño de datasets (30% local, 70% colab)
        f1_ponderado = (resultados_f1['local'] * 0.3) + (resultados_f1['colab'] * 0.7)
        
        print(f"\n🎯 RESULTADOS F1-SCORE PONDERADO:")
        print(f"🏠 Local:     {resultados_f1['local']:.4f} (30%)")
        print(f"☁️ Colab:     {resultados_f1['colab']:.4f} (70%)")
        print(f"🧮 Ponderado: {f1_ponderado:.4f}")
        
        resultados_f1['ponderado'] = f1_ponderado
        
        # Guardar resultados
        df_resultados = pd.DataFrame({
            'Dataset': ['Local', 'Colab', 'Ponderado'],
            'F1_Score': [resultados_f1['local'], resultados_f1['colab'], f1_ponderado],
            'Peso': [0.3, 0.7, 1.0]
        })
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_resultados = f'f1_ponderado_{timestamp}.csv'
        df_resultados.to_csv(archivo_resultados, index=False)
        print(f"💾 Resultados guardados: {archivo_resultados}")
    
    return resultados_f1

# ================================
# 🎮 FUNCIONES DE CONVENIENCIA
# ================================

def obtener_score_simple(archivo_csv):
    """Función simplificada - solo devuelve F1-Score"""
    _, f1 = obtener_score(archivo_csv)
    return f1

def obtener_predicciones_simple(archivo_csv):
    """Función simplificada - solo devuelve predicciones"""
    pred, _ = obtener_score(archivo_csv)
    return pred

# ================================
# 📋 ACTUALIZACIÓN DE EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    print("🎯 MÓDULO CALCULARF1_SCORE - VERSIÓN SIMPLIFICADA")
    print("="*60)
    print("📝 Ejemplos de uso principales:")
    print()
    print("# 1. USO BÁSICO - Obtener F1-Score")
    print("import calcularf1_score as cf1")
    print()
    print("# Para test_public.csv (tiene target 'Condición')")
    print("predicciones_public, f1_public = cf1.obtener_score('test_public.csv')")
    print()
    print("# Para test_private.csv (sin target)")
    print("predicciones_private, _ = cf1.obtener_score('test_private.csv')")
    print()
    print("# 2. USO SIMPLE - Solo F1-Score")
    print("f1_public = cf1.obtener_score_simple('test_public.csv')")
    print()
    print("# 3. GENERAR ARCHIVOS DE SUBMISSION")
    print("cf1.generar_predicciones('test_private.csv', 'solucion.csv')")
    print()
    print("# 4. PROCESAR TODO AUTOMÁTICAMENTE")
    print("resultados = cf1.procesar_ambos_datasets()")
    print()
    print("# 5. CALCULAR F1 PONDERADO (LOCAL VS COLAB)")
    print("f1_ponderado = cf1.calcular_f1_ponderado_datasets()")
    print("="*60)
    print()
    print("🚀 EJECUTANDO EJEMPLO AUTOMÁTICO...")
    
    try:
        # Intentar procesar automáticamente
        resultados = procesar_ambos_datasets()
        
        print("\n✅ PROCESO COMPLETADO:")
        for dataset, datos in resultados.items():
            if dataset != 'submission_final':
                print(f"  📊 {dataset.upper()}: F1={datos.get('f1_score', 'N/A')}")
        
        if 'submission_final' in resultados:
            print(f"  📝 Submission final: {resultados['submission_final']['archivo']}")
            
    except Exception as e:
        print(f"\n⚠️ No se pudo ejecutar automáticamente: {e}")
        print("💡 Asegúrate de tener los archivos de entrenamiento y test disponibles")