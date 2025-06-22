#!/usr/bin/env python3
"""
ejemplo_uso_calcularf1.py - Script de ejemplo para usar el módulo calcularf1_score

Este script muestra cómo usar todas las funcionalidades del módulo para:
1. Entrenar modelos con datasets separados
2. Obtener F1-Score de test_public.csv
3. Generar predicciones para test_private.csv
4. Calcular F1-Score ponderado entre local y colab
5. Crear archivos de submission
"""

import automatizacion.calcularf1_score as cf1
import pandas as pd

def main():
    print("🚀 EJEMPLO DE USO - CALCULARF1_SCORE")
    print("="*60)
    
    # ================================
    # 1. USO BÁSICO - OBTENER F1-SCORE
    # ================================
    
    print("\n📊 1. OBTENIENDO F1-SCORE DE TEST_PUBLIC:")
    try:
        # Para test_public.csv (tiene columna 'Condición')
        predicciones_public, f1_public = cf1.obtener_score('test_public.csv')
        print(f"✅ F1-Score test_public: {f1_public:.4f}")
        print(f"📊 Predicciones generadas: {len(predicciones_public):,}")
        
    except Exception as e:
        print(f"❌ Error con test_public: {e}")
    
    # ================================
    # 2. GENERAR PREDICCIONES PARA SUBMISSION
    # ================================
    
    print("\n📝 2. GENERANDO PREDICCIONES PARA TEST_PRIVATE:")
    try:
        # Para test_private.csv (sin columna 'Condición')
        predicciones_private, _ = cf1.obtener_score('test_private.csv', tiene_target=False)
        print(f"✅ Predicciones test_private: {len(predicciones_private):,}")
          # Generar archivo de submission
        submission = cf1.generar_predicciones('test_private.csv', 'solucion.csv')
        print(f"📝 Archivo de submission creado: solucion.csv")
        
    except Exception as e:
        print(f"❌ Error con test_private: {e}")
    
    # ================================
    # 3. PROCESAR TODO AUTOMÁTICAMENTE
    # ================================
    
    print("\n🤖 3. PROCESAMIENTO AUTOMÁTICO COMPLETO:")
    try:
        resultados = cf1.procesar_ambos_datasets()
        
        print("✅ Resultados del procesamiento automático:")
        for dataset, datos in resultados.items():
            if dataset != 'submission_final':
                f1_score = datos.get('f1_score')
                archivo = datos.get('archivo', 'N/A')
                print(f"  📊 {dataset.upper()}: {archivo} - F1: {f1_score if f1_score else 'N/A'}")
        
        if 'submission_final' in resultados:
            print(f"  📝 Submission combinada: {resultados['submission_final']['archivo']}")
            
    except Exception as e:
        print(f"❌ Error en procesamiento automático: {e}")
    
    # ================================
    # 4. CALCULAR F1 PONDERADO (SI TIENES AMBOS DATASETS)
    # ================================
    
    print("\n🧮 4. F1-SCORE PONDERADO ENTRE LOCAL Y COLAB:")
    try:
        resultados_ponderado = cf1.calcular_f1_ponderado_datasets()
        
        if 'ponderado' in resultados_ponderado:
            print("✅ F1-Score ponderado calculado:")
            print(f"  🏠 Local: {resultados_ponderado.get('local', 'N/A'):.4f} (30%)")
            print(f"  ☁️ Colab: {resultados_ponderado.get('colab', 'N/A'):.4f} (70%)")
            print(f"  🎯 Ponderado: {resultados_ponderado['ponderado']:.4f}")
        else:
            print("⚠️ No se pudo calcular F1 ponderado - faltan archivos de entrenamiento")
            
    except Exception as e:
        print(f"❌ Error en F1 ponderado: {e}")
    
    # ================================
    # 5. USO SIMPLIFICADO - SOLO OBTENER VALORES
    # ================================
    
    print("\n⚡ 5. USO SIMPLIFICADO:")
    try:
        # Solo obtener F1-Score
        f1_simple = cf1.obtener_score_simple('test_public.csv')
        print(f"✅ F1-Score simple: {f1_simple:.4f}")
        
        # Solo obtener predicciones
        pred_simple = cf1.obtener_predicciones_simple('test_private.csv')
        print(f"✅ Predicciones simples: {len(pred_simple):,} filas")
        
    except Exception as e:
        print(f"❌ Error en uso simplificado: {e}")
    
    print("\n🎉 EJEMPLO COMPLETADO")
    print("="*60)

def ejemplo_uso_colab():
    """
    Ejemplo específico para usar en Google Colab
    """
    print("☁️ EJEMPLO PARA GOOGLE COLAB")
    print("="*40)
    
    # En Colab, puedes usar train_colab.csv
    print("# En Google Colab, ejecuta:")
    print("import calcularf1_score as cf1")
    print()
    print("# Obtener F1 con dataset de Colab")
    print("modelo_colab = cf1.entrenar_modelo_completo('train_colab.csv')")
    print("pred_public, f1_colab = cf1.obtener_score('test_public.csv', modelo_colab)")
    print("print(f'F1-Score Colab: {f1_colab:.4f}')")
    print()
    print("# Generar predicciones")
    print("cf1.generar_predicciones('test_private.csv', 'submission_colab.csv', modelo_colab)")

if __name__ == "__main__":
    main()
    print("\n" + "="*60)
    ejemplo_uso_colab()
