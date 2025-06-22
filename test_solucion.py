#!/usr/bin/env python3
# ================================
# 🧪 SCRIPT DE PRUEBA - GENERACIÓN DE SOLUCION.CSV
# ================================
# Verifica que el sistema genere correctamente "solucion.csv"

import sys
import os

# Agregar ruta del proyecto
sys.path.append('.')
sys.path.append('./automatizacion')

try:
    import calcularf1_score as cf1
    print("✅ Módulo calcularf1_score importado correctamente")
    
    # Verificar archivos necesarios
    archivos_requeridos = ['test_public.csv', 'test_private.csv', 'train.csv']
    archivos_faltantes = [f for f in archivos_requeridos if not os.path.exists(f)]
    
    if archivos_faltantes:
        print(f"⚠️ Archivos faltantes: {archivos_faltantes}")
        print("📝 Creando archivos de prueba...")
        
        # Crear archivos de prueba básicos
        import pandas as pd
        import numpy as np
        
        # Crear datos de prueba
        np.random.seed(42)
        n_samples = 100
        
        # Dataset de entrenamiento con target
        train_data = {
            'ID': range(1, n_samples + 1),
            'Feature1': np.random.randn(n_samples),
            'Feature2': np.random.randn(n_samples),
            'Feature3': np.random.choice(['A', 'B', 'C'], n_samples),
            'Condición': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        }
        pd.DataFrame(train_data).to_csv('train.csv', index=False)
        print("✅ train.csv creado")
        
        # Dataset de test público con target (para validación)
        test_public_data = {
            'ID': range(n_samples + 1, n_samples + 51),
            'Feature1': np.random.randn(50),
            'Feature2': np.random.randn(50),
            'Feature3': np.random.choice(['A', 'B', 'C'], 50),
            'Condición': np.random.choice([0, 1], 50, p=[0.8, 0.2])
        }
        pd.DataFrame(test_public_data).to_csv('test_public.csv', index=False)
        print("✅ test_public.csv creado")
        
        # Dataset de test privado sin target (para submission)
        test_private_data = {
            'ID': range(n_samples + 51, n_samples + 101),
            'Feature1': np.random.randn(50),
            'Feature2': np.random.randn(50),
            'Feature3': np.random.choice(['A', 'B', 'C'], 50)
        }
        pd.DataFrame(test_private_data).to_csv('test_private.csv', index=False)
        print("✅ test_private.csv creado")
    
    print("\n🧪 INICIANDO PRUEBAS...")
    
    # PRUEBA 1: Procesar ambos datasets automáticamente
    print("\n1️⃣ PRUEBA: procesar_ambos_datasets()")
    try:
        resultados = cf1.procesar_ambos_datasets()
        
        if 'submission_final' in resultados:
            archivo_generado = resultados['submission_final']['archivo']
            print(f"✅ Archivo generado: {archivo_generado}")
            
            if archivo_generado == 'solucion.csv':
                print("🎉 ¡PERFECTO! El archivo se llama 'solucion.csv'")
            else:
                print(f"❌ ERROR: Se esperaba 'solucion.csv', pero se generó '{archivo_generado}'")
            
            # Verificar que el archivo existe
            if os.path.exists(archivo_generado):
                print(f"✅ El archivo {archivo_generado} existe en disco")
                
                # Verificar contenido
                df_solucion = pd.read_csv(archivo_generado)
                print(f"📊 Filas en {archivo_generado}: {len(df_solucion)}")
                print(f"📊 Columnas: {list(df_solucion.columns)}")
                
                if set(df_solucion.columns) == {'ID', 'Condición'}:
                    print("✅ Columnas correctas: ID, Condición")
                else:
                    print("❌ ERROR: Columnas incorrectas")
                    
        else:
            print("❌ ERROR: No se generó submission_final")
            
    except Exception as e:
        print(f"❌ ERROR en procesar_ambos_datasets(): {e}")
    
    # PRUEBA 2: Crear submission final manualmente
    print("\n2️⃣ PRUEBA: crear_submission_final()")
    try:
        # Simular predicciones
        pred_public = pd.DataFrame({
            'ID': range(101, 151),
            'Condición': np.random.choice([0, 1], 50)
        })
        
        pred_private = pd.DataFrame({
            'ID': range(151, 201),
            'Condición': np.random.choice([0, 1], 50)
        })
        
        # Crear submission final
        submission = cf1.crear_submission_final(pred_public, pred_private)
        
        if os.path.exists('solucion.csv'):
            print("✅ solucion.csv creado correctamente")
            
            df_check = pd.read_csv('solucion.csv')
            print(f"📊 Filas en solucion.csv: {len(df_check)}")
            print(f"📊 Distribución: {df_check['Condición'].value_counts().to_dict()}")
        else:
            print("❌ ERROR: solucion.csv no fue creado")
            
    except Exception as e:
        print(f"❌ ERROR en crear_submission_final(): {e}")
    
    # PRUEBA 3: generar_predicciones directo
    print("\n3️⃣ PRUEBA: generar_predicciones()")
    try:
        if os.path.exists('test_private.csv'):
            submission = cf1.generar_predicciones('test_private.csv', 'solucion_test.csv')
            
            if os.path.exists('solucion_test.csv'):
                print("✅ solucion_test.csv creado correctamente")
                os.remove('solucion_test.csv')  # Limpiar
            else:
                print("❌ ERROR: solucion_test.csv no fue creado")
                
    except Exception as e:
        print(f"❌ ERROR en generar_predicciones(): {e}")
    
    print("\n🎉 PRUEBAS COMPLETADAS")
    print("="*50)
    
    # Verificación final
    if os.path.exists('solucion.csv'):
        print("✅ ÉXITO: El archivo 'solucion.csv' está listo para subir a NeuroKup")
        
        # Mostrar información del archivo
        df_final = pd.read_csv('solucion.csv')
        print(f"📊 Archivo final: {len(df_final)} predicciones")
        print(f"📊 Rango de IDs: {df_final['ID'].min()} - {df_final['ID'].max()}")
        print(f"📊 Distribución de clases: {df_final['Condición'].value_counts().to_dict()}")
        
        # Verificar formato
        if all(col in df_final.columns for col in ['ID', 'Condición']):
            if df_final['Condición'].isin([0, 1]).all():
                print("✅ Formato correcto para NeuroKup: ID, Condición (0/1)")
            else:
                print("❌ ERROR: Valores de Condición no son 0/1")
        else:
            print("❌ ERROR: Faltan columnas ID o Condición")
    else:
        print("❌ ERROR: No se generó solucion.csv")

except ImportError as e:
    print(f"❌ ERROR: No se pudo importar calcularf1_score: {e}")
except Exception as e:
    print(f"❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()
