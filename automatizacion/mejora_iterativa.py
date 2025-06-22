# ================================
# 🚀 SISTEMA DE MEJORA ITERATIVA DEL MODELO
# ================================
# Estrategias avanzadas para optimizar F1-Score automáticamente

import pandas as pd
import numpy as np
import json
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Optimización
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, StratifiedKFold
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.calibration import CalibratedClassifierCV

# Modelos avanzados
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier, StackingClassifier, BaggingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# XGBoost y LightGBM (si están disponibles)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except:
    LIGHTGBM_AVAILABLE = False

# Balanceado de datos
try:
    from imblearn.over_sampling import SMOTE, ADASYN
    from imblearn.under_sampling import RandomUnderSampler
    from imblearn.combine import SMOTEENN
    IMBALANCED_AVAILABLE = True
except:
    IMBALANCED_AVAILABLE = False

import automatizacion.calcularf1_score as calcularf1_score

class ModeloMejorado:
    """Sistema de mejora iterativa del modelo"""
    
    def __init__(self, base_score=0.95):
        self.base_score = base_score
        self.mejor_modelo = None
        self.mejor_score = base_score
        self.historial_mejoras = []
        self.configuraciones_probadas = []
        
    def log_experimento(self, nombre_estrategia, score, parametros, tiempo_entrenamiento):
        """Registrar experimento en historial"""
        
        experimento = {
            'timestamp': datetime.now().isoformat(),
            'estrategia': nombre_estrategia,
            'f1_score': score,
            'parametros': parametros,
            'tiempo_entrenamiento': tiempo_entrenamiento,
            'mejora': score > self.mejor_score,
            'diferencia': score - self.mejor_score
        }
        
        self.historial_mejoras.append(experimento)
        
        if score > self.mejor_score:
            print(f"🎉 ¡MEJORA ENCONTRADA! {nombre_estrategia}")
            print(f"   Score anterior: {self.mejor_score:.4f}")
            print(f"   Score nuevo:    {score:.4f}")
            print(f"   Mejora:         +{score - self.mejor_score:.4f}")
            self.mejor_score = score
            return True
        else:
            print(f"❌ {nombre_estrategia}: {score:.4f} (sin mejora)")
            return False
    
    def hyperparameter_optimization(self, X, y):
        """Optimización de hiperparámetros con RandomizedSearch"""
        
        print("🔧 OPTIMIZACIÓN DE HIPERPARÁMETROS")
        print("="*40)
        
        inicio = datetime.now()
        
        # Configuraciones para diferentes modelos
        modelos_configs = {
            'RandomForest': {
                'modelo': RandomForestClassifier(random_state=42, class_weight='balanced'),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None]
                }
            }
        }
        
        # Añadir XGBoost si está disponible
        if XGBOOST_AVAILABLE:
            modelos_configs['XGBoost'] = {
                'modelo': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 6, 10],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }
            }
        
        # Añadir LightGBM si está disponible
        if LIGHTGBM_AVAILABLE:
            modelos_configs['LightGBM'] = {
                'modelo': lgb.LGBMClassifier(random_state=42, class_weight='balanced'),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 6, 10],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'num_leaves': [31, 50, 100],
                    'subsample': [0.8, 0.9, 1.0]
                }
            }
        
        mejor_modelo_local = None
        mejor_score_local = 0
        
        for nombre_modelo, config in modelos_configs.items():
            print(f"\n🔄 Optimizando {nombre_modelo}...")
            
            # RandomizedSearch para eficiencia
            search = RandomizedSearchCV(
                config['modelo'],
                config['params'],
                n_iter=20,  # 20 combinaciones aleatorias
                cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
                scoring='f1',
                n_jobs=-1,
                random_state=42
            )
            
            search.fit(X, y)
            
            score = search.best_score_
            print(f"   Mejor score: {score:.4f}")
            print(f"   Mejores parámetros: {search.best_params_}")
            
            if score > mejor_score_local:
                mejor_score_local = score
                mejor_modelo_local = search.best_estimator_
        
        tiempo_total = (datetime.now() - inicio).total_seconds()
        
        # Registrar experimento
        mejora = self.log_experimento(
            "Hyperparameter Optimization",
            mejor_score_local,
            {"tipo": "RandomizedSearchCV", "modelos_probados": list(modelos_configs.keys())},
            tiempo_total
        )
        
        if mejora:
            self.mejor_modelo = mejor_modelo_local
        
        return mejor_modelo_local, mejor_score_local
    
    def feature_engineering_avanzado(self, X, y):
        """Feature engineering automático y selección de features"""
        
        print("🧬 FEATURE ENGINEERING AVANZADO")
        print("="*40)
        
        inicio = datetime.now()
        
        X_original = X.copy()
        mejores_features = []
        
        # 1. Interacciones polinómicas
        print("🔄 Probando interacciones polinómicas...")
        poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        X_poly = poly.fit_transform(X.select_dtypes(include=[np.number]))
        
        # Limitamos features por rendimiento
        if X_poly.shape[1] > 1000:
            selector = SelectKBest(f_classif, k=500)
            X_poly = selector.fit_transform(X_poly, y)
        
        X_poly_df = pd.DataFrame(X_poly, index=X.index)
        X_with_poly = pd.concat([X, X_poly_df], axis=1)
        
        score_poly = self._evaluar_features(X_with_poly, y, "Polynomial Features")
        mejores_features.append(('polynomial', score_poly, X_with_poly))
        
        # 2. Selección de features con RFE
        print("🔄 Probando selección de features (RFE)...")
        estimator = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced')
        
        # Probar diferentes números de features
        for n_features in [int(X.shape[1] * 0.5), int(X.shape[1] * 0.75), int(X.shape[1] * 0.9)]:
            if n_features > 5:
                selector = RFE(estimator, n_features_to_select=n_features)
                X_rfe = selector.fit_transform(X, y)
                X_rfe_df = pd.DataFrame(X_rfe, index=X.index)
                
                score_rfe = self._evaluar_features(X_rfe_df, y, f"RFE_{n_features}_features")
                mejores_features.append((f'rfe_{n_features}', score_rfe, X_rfe_df))
        
        # 3. SelectKBest con diferentes valores de k
        print("🔄 Probando SelectKBest...")
        for k in [10, 20, 50]:
            if k <= X.shape[1]:
                selector = SelectKBest(f_classif, k=k)
                X_kbest = selector.fit_transform(X, y)
                X_kbest_df = pd.DataFrame(X_kbest, index=X.index)
                
                score_kbest = self._evaluar_features(X_kbest_df, y, f"SelectKBest_k{k}")
                mejores_features.append((f'kbest_{k}', score_kbest, X_kbest_df))
        
        tiempo_total = (datetime.now() - inicio).total_seconds()
        
        # Encontrar el mejor conjunto de features
        mejor_features = max(mejores_features, key=lambda x: x[1])
        
        self.log_experimento(
            "Feature Engineering Avanzado",
            mejor_features[1],
            {"mejor_estrategia": mejor_features[0], "num_features": mejor_features[2].shape[1]},
            tiempo_total
        )
        
        return mejor_features[2], mejor_features[1]
    
    def _evaluar_features(self, X, y, nombre_estrategia):
        """Evaluar conjunto de features con validación cruzada"""
        
        modelo = RandomForestClassifier(
            n_estimators=100, 
            random_state=42, 
            class_weight='balanced'
        )
        
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = cross_val_score(modelo, X, y, cv=cv, scoring='f1')
        score_promedio = scores.mean()
        
        print(f"   {nombre_estrategia}: {score_promedio:.4f}")
        return score_promedio
    
    def ensemble_avanzado(self, X, y):
        """Crear ensemble sofisticado con múltiples niveles"""
        
        print("🤖 ENSEMBLE AVANZADO")
        print("="*40)
        
        inicio = datetime.now()
        
        # Modelos base diversos
        modelos_base = [
            ('rf', RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')),
            ('et', ExtraTreesClassifier(n_estimators=200, random_state=42, class_weight='balanced')),
            ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
            ('lr', LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000))
        ]
        
        # Añadir XGBoost si está disponible
        if XGBOOST_AVAILABLE:
            modelos_base.append(('xgb', xgb.XGBClassifier(random_state=42, eval_metric='logloss')))
        
        # Añadir LightGBM si está disponible
        if LIGHTGBM_AVAILABLE:
            modelos_base.append(('lgb', lgb.LGBMClassifier(random_state=42, class_weight='balanced')))
        
        mejores_ensembles = []
        
        # 1. Voting Classifier (soft voting)
        print("🔄 Probando Voting Classifier...")
        voting_clf = VotingClassifier(modelos_base, voting='soft')
        score_voting = self._evaluar_modelo(voting_clf, X, y)
        mejores_ensembles.append(('voting', score_voting, voting_clf))
        
        # 2. Stacking Classifier
        print("🔄 Probando Stacking Classifier...")
        stacking_clf = StackingClassifier(
            modelos_base,
            final_estimator=LogisticRegression(class_weight='balanced', random_state=42),
            cv=3
        )
        score_stacking = self._evaluar_modelo(stacking_clf, X, y)
        mejores_ensembles.append(('stacking', score_stacking, stacking_clf))
        
        # 3. Bagging de diferentes modelos
        print("🔄 Probando Bagging Ensembles...")
        for nombre, modelo in modelos_base[:3]:  # Solo los primeros 3 por eficiencia
            bagging_clf = BaggingClassifier(
                modelo, 
                n_estimators=10, 
                random_state=42,
                n_jobs=-1
            )
            score_bagging = self._evaluar_modelo(bagging_clf, X, y)
            mejores_ensembles.append((f'bagging_{nombre}', score_bagging, bagging_clf))
        
        tiempo_total = (datetime.now() - inicio).total_seconds()
        
        # Mejor ensemble
        mejor_ensemble = max(mejores_ensembles, key=lambda x: x[1])
        
        mejora = self.log_experimento(
            "Ensemble Avanzado",
            mejor_ensemble[1],
            {"mejor_tipo": mejor_ensemble[0], "num_modelos_base": len(modelos_base)},
            tiempo_total
        )
        
        if mejora:
            self.mejor_modelo = mejor_ensemble[2]
        
        return mejor_ensemble[2], mejor_ensemble[1]
    
    def _evaluar_modelo(self, modelo, X, y):
        """Evaluar modelo con validación cruzada"""
        
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = cross_val_score(modelo, X, y, cv=cv, scoring='f1')
        return scores.mean()
    
    def balanceado_datos_avanzado(self, X, y):
        """Técnicas avanzadas para manejar desbalance"""
        
        if not IMBALANCED_AVAILABLE:
            print("⚠️ imblearn no disponible, saltando balanceado avanzado")
            return X, y, 0
        
        print("⚖️ BALANCEADO DE DATOS AVANZADO")
        print("="*40)
        
        inicio = datetime.now()
        
        # Solo usar columnas numéricas para SMOTE
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X_numeric = X[numeric_cols]
        
        if X_numeric.shape[1] == 0:
            print("❌ No hay columnas numéricas para SMOTE")
            return X, y, 0
        
        mejores_balanceados = []
        
        # 1. SMOTE básico
        print("🔄 Probando SMOTE...")
        try:
            smote = SMOTE(random_state=42)
            X_smote, y_smote = smote.fit_resample(X_numeric, y)
            score_smote = self._evaluar_datos_balanceados(X_smote, y_smote)
            mejores_balanceados.append(('smote', score_smote, X_smote, y_smote))
        except Exception as e:
            print(f"   Error con SMOTE: {e}")
        
        # 2. ADASYN
        print("🔄 Probando ADASYN...")
        try:
            adasyn = ADASYN(random_state=42)
            X_adasyn, y_adasyn = adasyn.fit_resample(X_numeric, y)
            score_adasyn = self._evaluar_datos_balanceados(X_adasyn, y_adasyn)
            mejores_balanceados.append(('adasyn', score_adasyn, X_adasyn, y_adasyn))
        except Exception as e:
            print(f"   Error con ADASYN: {e}")
        
        # 3. SMOTEENN (combinación)
        print("🔄 Probando SMOTEENN...")
        try:
            smoteenn = SMOTEENN(random_state=42)
            X_smoteenn, y_smoteenn = smoteenn.fit_resample(X_numeric, y)
            score_smoteenn = self._evaluar_datos_balanceados(X_smoteenn, y_smoteenn)
            mejores_balanceados.append(('smoteenn', score_smoteenn, X_smoteenn, y_smoteenn))
        except Exception as e:
            print(f"   Error con SMOTEENN: {e}")
        
        tiempo_total = (datetime.now() - inicio).total_seconds()
        
        if mejores_balanceados:
            mejor_balanceado = max(mejores_balanceados, key=lambda x: x[1])
            
            self.log_experimento(
                "Balanceado Avanzado",
                mejor_balanceado[1],
                {"mejor_tecnica": mejor_balanceado[0], "tamaño_final": len(mejor_balanceado[3])},
                tiempo_total
            )
            
            return mejor_balanceado[2], mejor_balanceado[3], mejor_balanceado[1]
        else:
            return X, y, 0
    
    def _evaluar_datos_balanceados(self, X, y):
        """Evaluar datos balanceados"""
        
        modelo = RandomForestClassifier(
            n_estimators=50, 
            random_state=42, 
            class_weight='balanced'
        )
        
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = cross_val_score(modelo, X, y, cv=cv, scoring='f1')
        score_promedio = scores.mean()
        
        print(f"   Score: {score_promedio:.4f}")
        return score_promedio
    
    def threshold_optimization_avanzado(self, modelo, X, y):
        """Optimización avanzada de threshold"""
        
        print("🎚️ OPTIMIZACIÓN AVANZADA DE THRESHOLD")
        print("="*40)
        
        inicio = datetime.now()
        
        # Validación cruzada para threshold
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        mejores_thresholds = []
        
        for fold, (train_idx, val_idx) in enumerate(cv.split(X, y)):
            X_train_fold, X_val_fold = X.iloc[train_idx], X.iloc[val_idx]
            y_train_fold, y_val_fold = y.iloc[train_idx], y.iloc[val_idx]
            
            # Entrenar modelo en fold
            modelo.fit(X_train_fold, y_train_fold)
            y_proba = modelo.predict_proba(X_val_fold)[:, 1]
            
            # Encontrar mejor threshold para este fold
            thresholds = np.arange(0.1, 0.9, 0.01)
            mejores_f1_fold = []
            
            for thresh in thresholds:
                y_pred = (y_proba >= thresh).astype(int)
                f1 = f1_score(y_val_fold, y_pred)
                mejores_f1_fold.append((thresh, f1))
            
            mejor_thresh_fold = max(mejores_f1_fold, key=lambda x: x[1])
            mejores_thresholds.append(mejor_thresh_fold)
        
        # Promedio de mejores thresholds
        threshold_optimo = np.mean([t[0] for t in mejores_thresholds])
        f1_promedio = np.mean([t[1] for t in mejores_thresholds])
        
        tiempo_total = (datetime.now() - inicio).total_seconds()
        
        self.log_experimento(
            "Threshold Optimization Avanzado",
            f1_promedio,
            {"threshold_optimo": threshold_optimo, "cv_folds": 5},
            tiempo_total
        )
        
        print(f"🎯 Threshold óptimo: {threshold_optimo:.3f}")
        print(f"🏆 F1-Score esperado: {f1_promedio:.4f}")
        
        return threshold_optimo, f1_promedio
    
    def ejecutar_todas_estrategias(self, X, y):
        """Ejecutar todas las estrategias de mejora secuencialmente"""
        
        print("🚀 EJECUTANDO TODAS LAS ESTRATEGIAS DE MEJORA")
        print("="*60)
        print(f"🎯 Score base a superar: {self.base_score:.4f}")
        print()
        
        X_actual, y_actual = X.copy(), y.copy()
        
        # 1. Feature Engineering
        print("1️⃣ FEATURE ENGINEERING AVANZADO")
        X_mejorado, score_fe = self.feature_engineering_avanzado(X_actual, y_actual)
        if score_fe > self._evaluar_features(X_actual, y_actual, "Original"):
            X_actual = X_mejorado
            print("   ✅ Features mejorados adoptados")
        else:
            print("   ❌ Features originales mantenidos")
        
        # 2. Balanceado de datos
        print("\n2️⃣ BALANCEADO DE DATOS AVANZADO")
        X_balanced, y_balanced, score_balance = self.balanceado_datos_avanzado(X_actual, y_actual)
        if score_balance > self._evaluar_features(X_actual, y_actual, "Sin balancear"):
            X_actual, y_actual = X_balanced, y_balanced
            print("   ✅ Datos balanceados adoptados")
        else:
            print("   ❌ Datos originales mantenidos")
        
        # 3. Optimización de hiperparámetros
        print("\n3️⃣ OPTIMIZACIÓN DE HIPERPARÁMETROS")
        modelo_optimizado, score_hp = self.hyperparameter_optimization(X_actual, y_actual)
        
        # 4. Ensemble avanzado
        print("\n4️⃣ ENSEMBLE AVANZADO")
        modelo_ensemble, score_ensemble = self.ensemble_avanzado(X_actual, y_actual)
        
        # 5. Threshold optimization
        if hasattr(self.mejor_modelo, 'predict_proba'):
            print("\n5️⃣ OPTIMIZACIÓN DE THRESHOLD")
            threshold_opt, score_threshold = self.threshold_optimization_avanzado(self.mejor_modelo, X_actual, y_actual)
        
        # Resumen final
        print("\n" + "="*60)
        print("🏆 RESUMEN DE MEJORAS")
        print("="*60)
        
        mejoras_significativas = [exp for exp in self.historial_mejoras if exp['mejora']]
        
        if mejoras_significativas:
            print(f"✅ Se encontraron {len(mejoras_significativas)} mejoras:")
            for mejora in mejoras_significativas:
                print(f"   🎯 {mejora['estrategia']}: {mejora['f1_score']:.4f} (+{mejora['diferencia']:.4f})")
            
            print(f"\n🏆 MEJOR SCORE ALCANZADO: {self.mejor_score:.4f}")
            print(f"📈 MEJORA TOTAL: +{self.mejor_score - self.base_score:.4f}")
        else:
            print("❌ No se encontraron mejoras significativas")
            print("💡 Considera probar con diferentes datasets o estrategias adicionales")
        
        return self.mejor_modelo, self.mejor_score
    
    def guardar_resultados(self, filename='mejoras_modelo.json'):
        """Guardar historial de mejoras"""
        
        resultado = {
            'base_score': self.base_score,
            'mejor_score': self.mejor_score,
            'mejora_total': self.mejor_score - self.base_score,
            'timestamp': datetime.now().isoformat(),
            'historial_mejoras': self.historial_mejoras,
            'configuraciones_probadas': self.configuraciones_probadas
        }
        
        with open(filename, 'w') as f:
            json.dump(resultado, f, indent=2, default=str)
        
        print(f"💾 Resultados guardados en: {filename}")
        
        return filename

# ================================
# 🎮 FUNCIONES PRINCIPALES
# ================================

def mejorar_modelo_automatico(archivo_train='train.csv', score_base=None):
    """
    Función principal para mejorar modelo automáticamente
    
    Args:
        archivo_train: Archivo de entrenamiento
        score_base: Score base a superar (se calcula automáticamente si es None)
    
    Returns:
        tuple: (mejor_modelo, mejor_score, historial_mejoras)
    """
    
    print("🚀 MEJORA AUTOMÁTICA DEL MODELO")
    print("="*50)
    
    # Cargar datos
    df = pd.read_csv(archivo_train)
    print(f"📊 Dataset cargado: {df.shape}")
    
    # Preparar datos (usando función de calcularf1_score)
    modelo_base = calcularf1_score.ModeloCoronario()
    df_clean = modelo_base.limpiar_datos(df)
    df_imputed = modelo_base.imputar_nulos(df_clean)
    df_features = modelo_base.feature_engineering(df_imputed)
    
    X, y = modelo_base.preparar_para_ml(df_features, es_entrenamiento=True)
    
    # Calcular score base si no se proporciona
    if score_base is None:
        modelo_baseline = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores_base = cross_val_score(modelo_baseline, X, y, cv=cv, scoring='f1')
        score_base = scores_base.mean()
        print(f"🎯 Score base calculado: {score_base:.4f}")
    
    # Crear sistema de mejora
    sistema_mejora = ModeloMejorado(base_score=score_base)
    
    # Ejecutar todas las estrategias
    mejor_modelo, mejor_score = sistema_mejora.ejecutar_todas_estrategias(X, y)
    
    # Guardar resultados
    archivo_resultados = sistema_mejora.guardar_resultados()
    
    return mejor_modelo, mejor_score, sistema_mejora.historial_mejoras

def mejora_continua_programada(archivo_train='train.csv', intervalo_horas=6, max_iteraciones=10):
    """
    Sistema de mejora continua programada
    
    Args:
        archivo_train: Archivo de entrenamiento
        intervalo_horas: Horas entre iteraciones
        max_iteraciones: Máximo número de iteraciones
    """
    
    print("🔄 SISTEMA DE MEJORA CONTINUA")
    print("="*50)
    print(f"📅 Intervalo: {intervalo_horas} horas")
    print(f"🔢 Máximo iteraciones: {max_iteraciones}")
    
    mejor_score_global = 0
    iteracion = 0
    
    while iteracion < max_iteraciones:
        print(f"\n🚀 ITERACIÓN {iteracion + 1}/{max_iteraciones}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Ejecutar mejora
            modelo, score, historial = mejorar_modelo_automatico(archivo_train, mejor_score_global)
            
            # Actualizar mejor score
            if score > mejor_score_global:
                mejor_score_global = score
                
                # Guardar mejor modelo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                modelo_filename = f'mejor_modelo_{timestamp}.pkl'
                
                with open(modelo_filename, 'wb') as f:
                    pickle.dump(modelo, f)
                
                print(f"💾 Mejor modelo guardado: {modelo_filename}")
                print(f"🏆 Nuevo mejor score: {score:.4f}")
            
            iteracion += 1
            
            # Esperar siguiente iteración (en producción usarías un scheduler)
            if iteracion < max_iteraciones:
                print(f"⏱️ Esperando {intervalo_horas} horas para siguiente iteración...")
                # En lugar de time.sleep() en producción, usarías un cron job
                
        except Exception as e:
            print(f"❌ Error en iteración {iteracion + 1}: {e}")
            iteracion += 1
    
    print(f"\n🏁 MEJORA CONTINUA COMPLETADA")
    print(f"🏆 Mejor score alcanzado: {mejor_score_global:.4f}")

# ================================
# 📋 EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    print("🚀 SISTEMA DE MEJORA ITERATIVA")
    print("="*50)
    print("📝 Funciones disponibles:")
    print("  • mejorar_modelo_automatico(archivo_train)")
    print("  • mejora_continua_programada(archivo_train, intervalo_horas)")
    print()
    print("💡 Uso básico:")
    print("  mejor_modelo, mejor_score, historial = mejorar_modelo_automatico('train.csv')")
    print()
    print("🔄 Mejora continua:")
    print("  mejora_continua_programada('train.csv', intervalo_horas=6)")
    print("="*50)