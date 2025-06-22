#!/usr/bin/env python3
"""
analisis_ponderado.py - Script para análisis ponderado entre local y Colab

Este script implementa exactamente lo que describiste:
1. Analizar train_local.csv en el entorno local
2. Analizar train_colab.csv en Google Colab
3. Combinar resultados con ponderación 30% local, 70% Colab
4. Generar submission final
"""

import calcularf1_score as cf1
import pandas as pd
import os
from datetime import datetime

def analisis_local():
    """
    Análisis a ejecutar en el entorno LOCAL
    """
    print("🏠 ANÁLISIS LOCAL - TRAIN_LOCAL.CSV")
    print("="*50)
    
    try:
        # Entrenar modelo con dataset local
        print("🚀 Entrenando modelo con train_local.csv...")
        modelo_local = cf1.entrenar_modelo_completo('train_local.csv')
        
        # Evaluar en test_public
        print("📊 Evaluando en test_public.csv...")
        pred_public_local, f1_local = cf1.obtener_score('test_public.csv', modelo_local)
        
        # Generar predicciones para test_private
        print("📝 Generando predicciones para test_private.csv...")
        pred_private_local, _ = cf1.obtener_score('test_private.csv', modelo_local)
        
        # Guardar resultados locales
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar F1-Score local
        resultado_local = {
            'entorno': 'local',
            'dataset_entrenamiento': 'train_local.csv',
            'f1_score': f1_local,
            'timestamp': timestamp,
            'peso': 0.3
        }
        
        df_resultado = pd.DataFrame([resultado_local])
        df_resultado.to_csv(f'resultado_local_{timestamp}.csv', index=False)
        
        # Guardar predicciones
        pred_public_local.to_csv(f'predicciones_public_local_{timestamp}.csv', index=False)
        pred_private_local.to_csv(f'predicciones_private_local_{timestamp}.csv', index=False)
        
        print(f"✅ RESULTADO LOCAL:")
        print(f"   🎯 F1-Score: {f1_local:.4f}")
        print(f"   📊 Muestras entrenamiento: {len(pd.read_csv('train_local.csv')):,}")
        print(f"   💾 Archivos guardados con timestamp: {timestamp}")
        
        return {
            'f1_score': f1_local,
            'timestamp': timestamp,
            'predicciones_public': pred_public_local,
            'predicciones_private': pred_private_local
        }
        
    except Exception as e:
        print(f"❌ Error en análisis local: {e}")
        return None

def analisis_colab():
    """
    Análisis a ejecutar en GOOGLE COLAB
    
    NOTA: Copia este código a Google Colab y ejecútalo allí
    """
    print("☁️ ANÁLISIS COLAB - TRAIN_COLAB.CSV")
    print("="*50)
    
    try:
        # Entrenar modelo con dataset de Colab
        print("🚀 Entrenando modelo con train_colab.csv...")
        modelo_colab = cf1.entrenar_modelo_completo('train_colab.csv')
        
        # Evaluar en test_public
        print("📊 Evaluando en test_public.csv...")
        pred_public_colab, f1_colab = cf1.obtener_score('test_public.csv', modelo_colab)
        
        # Generar predicciones para test_private
        print("📝 Generando predicciones para test_private.csv...")
        pred_private_colab, _ = cf1.obtener_score('test_private.csv', modelo_colab)
        
        # Guardar resultados de Colab
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar F1-Score de Colab
        resultado_colab = {
            'entorno': 'colab',
            'dataset_entrenamiento': 'train_colab.csv',
            'f1_score': f1_colab,
            'timestamp': timestamp,
            'peso': 0.7
        }
        
        df_resultado = pd.DataFrame([resultado_colab])
        df_resultado.to_csv(f'resultado_colab_{timestamp}.csv', index=False)
        
        # Guardar predicciones
        pred_public_colab.to_csv(f'predicciones_public_colab_{timestamp}.csv', index=False)
        pred_private_colab.to_csv(f'predicciones_private_colab_{timestamp}.csv', index=False)
        
        print(f"✅ RESULTADO COLAB:")
        print(f"   🎯 F1-Score: {f1_colab:.4f}")
        print(f"   📊 Muestras entrenamiento: {len(pd.read_csv('train_colab.csv')):,}")
        print(f"   💾 Archivos guardados con timestamp: {timestamp}")
        
        return {
            'f1_score': f1_colab,
            'timestamp': timestamp,
            'predicciones_public': pred_public_colab,
            'predicciones_private': pred_private_colab
        }
        
    except Exception as e:
        print(f"❌ Error en análisis Colab: {e}")
        return None

def combinar_resultados(f1_local, f1_colab, pred_local=None, pred_colab=None):
    """
    Combina los resultados de local y Colab con ponderación
    """
    print("🧮 COMBINANDO RESULTADOS LOCAL + COLAB")
    print("="*50)
    
    # Calcular F1-Score ponderado
    peso_local = 0.3  # 30% para local (train_local.csv)
    peso_colab = 0.7  # 70% para Colab (train_colab.csv)
    
    f1_ponderado = (f1_local * peso_local) + (f1_colab * peso_colab)
    
    # Análisis de consistencia
    diferencia = abs(f1_local - f1_colab)
    mejor_entorno = "Local" if f1_local > f1_colab else "Colab"
    
    print(f"📊 RESULTADOS FINALES:")
    print(f"   🏠 F1-Score Local:  {f1_local:.4f} (peso: {peso_local})")
    print(f"   ☁️ F1-Score Colab:  {f1_colab:.4f} (peso: {peso_colab})")
    print(f"   🎯 F1-Score Ponderado: {f1_ponderado:.4f}")
    print(f"   📏 Diferencia: {diferencia:.4f}")
    print(f"   🏆 Mejor entorno: {mejor_entorno}")
    
    # Guardar resultado final
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    resultado_final = {
        'f1_local': f1_local,
        'f1_colab': f1_colab,
        'f1_ponderado': f1_ponderado,
        'peso_local': peso_local,
        'peso_colab': peso_colab,
        'diferencia': diferencia,
        'mejor_entorno': mejor_entorno,
        'timestamp': timestamp
    }
    
    df_final = pd.DataFrame([resultado_final])
    archivo_final = f'resultado_ponderado_final_{timestamp}.csv'
    df_final.to_csv(archivo_final, index=False)
    
    print(f"💾 Resultado final guardado: {archivo_final}")
    
    # Si hay predicciones, crear ensemble
    if pred_local is not None and pred_colab is not None:
        print("🤖 Creando ensemble de predicciones...")
        
        # Combinar predicciones con ponderación en las probabilidades
        pred_ensemble = pred_local.copy()
        
        # Ponderar probabilidades
        prob_ponderada = (pred_local['Probabilidad'] * peso_local) + (pred_colab['Probabilidad'] * peso_colab)
        
        # Nueva predicción basada en probabilidad ponderada
        pred_ensemble['Condición'] = (prob_ponderada >= 0.5).astype(int)
        pred_ensemble['Probabilidad'] = prob_ponderada
        
        # Guardar submission ensemble
        submission_ensemble = pred_ensemble[['ID', 'Condición']]
        archivo_submission = f'submission_ensemble_{timestamp}.csv'
        submission_ensemble.to_csv(archivo_submission, index=False)
        
        print(f"📝 Submission ensemble: {archivo_submission}")
        
        resultado_final['archivo_submission'] = archivo_submission
    
    return resultado_final

def ejecutar_analisis_completo():
    """
    Ejecuta el análisis completo en el entorno actual
    """
    print("🚀 ANÁLISIS PONDERADO COMPLETO")
    print("="*60)
    
    resultados = {}
    
    # Análisis local
    if os.path.exists('train_local.csv'):
        print("\n🏠 EJECUTANDO ANÁLISIS LOCAL:")
        resultado_local = analisis_local()
        if resultado_local:
            resultados['local'] = resultado_local
    else:
        print("⚠️ train_local.csv no encontrado - saltando análisis local")
    
    # Análisis Colab (solo si estamos en un entorno que lo permita)
    if os.path.exists('train_colab.csv'):
        print("\n☁️ EJECUTANDO ANÁLISIS COLAB:")
        resultado_colab = analisis_colab()
        if resultado_colab:
            resultados['colab'] = resultado_colab
    else:
        print("⚠️ train_colab.csv no encontrado - saltando análisis Colab")
    
    # Combinar si tenemos ambos
    if 'local' in resultados and 'colab' in resultados:
        print("\n🧮 COMBINANDO RESULTADOS:")
        resultado_final = combinar_resultados(
            f1_local=resultados['local']['f1_score'],
            f1_colab=resultados['colab']['f1_score'],
            pred_local=resultados['local']['predicciones_private'],
            pred_colab=resultados['colab']['predicciones_private']
        )
        resultados['final'] = resultado_final
    else:
        print("\n⚠️ No se pueden combinar resultados - falta algún dataset")
    
    return resultados

def generar_codigo_colab():
    """
    Genera el código Python para ejecutar en Google Colab
    """
    codigo_colab = '''
# ================================
# CÓDIGO PARA EJECUTAR EN GOOGLE COLAB
# ================================

# 1. Subir archivos necesarios a Colab:
#    - calcularf1_score.py
#    - train_colab.csv  
#    - test_public.csv
#    - test_private.csv

# 2. Ejecutar este código en Colab:

import calcularf1_score as cf1
import pandas as pd
from datetime import datetime

def analisis_colab():
    print("☁️ ANÁLISIS EN GOOGLE COLAB")
    print("="*40)
    
    # Entrenar con train_colab.csv
    modelo_colab = cf1.entrenar_modelo_completo('train_colab.csv')
    
    # Evaluar en test_public
    pred_public, f1_colab = cf1.obtener_score('test_public.csv', modelo_colab)
    
    # Predecir test_private
    pred_private, _ = cf1.obtener_score('test_private.csv', modelo_colab)
    
    # Guardar resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    resultado = {
        'entorno': 'colab',
        'f1_score': f1_colab,
        'timestamp': timestamp
    }
    
    df_resultado = pd.DataFrame([resultado])
    df_resultado.to_csv(f'resultado_colab_{timestamp}.csv', index=False)
    
    pred_private.to_csv(f'predicciones_colab_{timestamp}.csv', index=False)
    
    print(f"✅ F1-Score Colab: {f1_colab:.4f}")
    print(f"💾 Archivos guardados con timestamp: {timestamp}")
    
    # Descargar archivos desde Colab
    from google.colab import files
    files.download(f'resultado_colab_{timestamp}.csv')
    files.download(f'predicciones_colab_{timestamp}.csv')
    
    return f1_colab

# Ejecutar análisis
f1_colab = analisis_colab()
'''
    
    # Guardar código para Colab
    with open('codigo_para_colab.py', 'w', encoding='utf-8') as f:
        f.write(codigo_colab)
    
    print("📝 Código para Colab guardado en: codigo_para_colab.py")
    print("💡 Copia este archivo a Google Colab y ejecútalo allí")

if __name__ == "__main__":
    print("🎯 SCRIPT DE ANÁLISIS PONDERADO")
    print("="*60)
    print("Opciones:")
    print("1. Ejecutar análisis completo en entorno actual")
    print("2. Generar código para Google Colab")
    print("3. Solo análisis local")
    print("4. Solo combinar resultados existentes")
    
    opcion = input("\nSelecciona opción (1-4): ").strip()
    
    if opcion == "1":
        resultados = ejecutar_analisis_completo()
        print(f"\n✅ Análisis completado. Resultados: {list(resultados.keys())}")
        
    elif opcion == "2":
        generar_codigo_colab()
        
    elif opcion == "3":
        if os.path.exists('train_local.csv'):
            resultado_local = analisis_local()
            print(f"✅ Análisis local completado: F1 = {resultado_local['f1_score']:.4f}")
        else:
            print("❌ train_local.csv no encontrado")
            
    elif opcion == "4":
        f1_local = float(input("Ingresa F1-Score local: "))
        f1_colab = float(input("Ingresa F1-Score Colab: "))
        resultado = combinar_resultados(f1_local, f1_colab)
        print(f"✅ F1 ponderado: {resultado['f1_ponderado']:.4f}")
        
    else:
        print("❌ Opción no válida")
