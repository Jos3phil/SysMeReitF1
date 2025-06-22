#!/usr/bin/env python3
"""
split.py - Dividir dataset para competencia Neuro-Kup

Uso:
    python split.py
    
Genera:
    - train_colab.csv (70% del total)
    - train_local.csv (30% del total)
"""

import pandas as pd
from sklearn.model_selection import train_test_split
import os
import sys

# ================================
# 🔧 CONFIGURACIÓN
# ================================

# Archivos
INPUT_FILE = 'train.csv'  # Cambia si tu archivo tiene otro nombre
TARGET_COLUMN = None      # Si es None, busca automáticamente

# Parámetros de división
LOCAL_SIZE = 0.3              # 30% para local, 70% para colab
RANDOM_STATE = 42

# ================================
# 🔍 FUNCIONES AUXILIARES
# ================================

def encontrar_target_automatico(df):
    """Busca automáticamente la columna target"""
    posibles_targets = [
        'target', 'enfermedad', 'coronaria', 'clase', 'label', 'y',
        'target_column', 'diagnosis', 'disease', 'outcome', 'condición', 'condicion'
    ]
    
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in posibles_targets:
            return col
        if any(palabra in col_lower for palabra in ['target', 'enfermedad', 'coronaria', 'condición', 'condicion']):
            return col
    
    # Si no encuentra, usar la última columna
    print(f"⚠️  No se encontró target automáticamente. Usando última columna: '{df.columns[-1]}'")
    return df.columns[-1]

def verificar_archivo(filepath):
    """Verificar que el archivo existe"""
    if not os.path.exists(filepath):
        print(f"❌ Error: No se encuentra el archivo '{filepath}'")
        print(f"   Archivos en directorio actual:")
        for archivo in os.listdir('.'):
            if archivo.endswith('.csv'):
                print(f"     - {archivo}")
        return False
    return True

def mostrar_info_dataset(df, target_col):
    """Mostrar información del dataset"""
    print(f"📊 INFORMACIÓN DEL DATASET")
    print("="*40)
    print(f"Archivo: {INPUT_FILE}")
    print(f"Dimensiones: {df.shape[0]:,} filas × {df.shape[1]} columnas")
    print(f"Target: '{target_col}'")
    
    # Distribución del target
    dist = df[target_col].value_counts()
    print(f"Distribución del target:")
    for valor, cantidad in dist.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"  {valor}: {cantidad:,} ({porcentaje:.1f}%)")
    
    # Verificar balance
    if len(dist) == 2:
        ratio = min(dist) / max(dist)
        if ratio < 0.3:
            print(f"⚠️  Dataset desbalanceado (ratio: {ratio:.2f})")
        else:
            print(f"✅ Balance aceptable (ratio: {ratio:.2f})")
    
    print("="*40)

def dividir_dataset(df, target_col):
    """Dividir el dataset en dos partes para comparación directa entre entornos"""
    print(f"\n🔄 DIVIDIENDO DATASET...")
    
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    
    # División directa: Train Colab (70%) vs Train Local (30%)
    X_train_colab, X_train_local, y_train_colab, y_train_local = train_test_split(
        X, y,
        test_size=LOCAL_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    # Reconstruir DataFrames
    train_colab = pd.concat([X_train_colab, y_train_colab], axis=1)
    train_local = pd.concat([X_train_local, y_train_local], axis=1)
    
    # Mostrar resultados
    print(f"✅ División completada:")
    print(f"  Train Colab:   {len(train_colab):,} muestras ({len(train_colab)/len(df)*100:.1f}%)")
    print(f"  Train Local:   {len(train_local):,} muestras ({len(train_local)/len(df)*100:.1f}%)")
    
    return train_colab, train_local

def verificar_distribuciones(train_colab, train_local, target_col):
    """Verificar que las distribuciones se mantienen"""
    print(f"\n📈 VERIFICANDO DISTRIBUCIONES:")
    
    distribuciones = {}
    for nombre, data in [('Colab', train_colab), ('Local', train_local)]:
        dist = data[target_col].value_counts(normalize=True).sort_index()
        distribuciones[nombre] = dist
    
    df_dist = pd.DataFrame(distribuciones).round(3)
    print(df_dist)
    
    # Verificar consistencia
    std_dev = df_dist.std(axis=1).max()
    if std_dev < 0.05:
        print(f"✅ Distribuciones consistentes (desv. std máx: {std_dev:.3f})")
    else:
        print(f"⚠️  Distribuciones variables (desv. std máx: {std_dev:.3f})")

def guardar_archivos(train_colab, train_local):
    """Guardar los archivos divididos"""
    print(f"\n💾 GUARDANDO ARCHIVOS...")
    
    archivos = [
        ('train_colab.csv', train_colab),
        ('train_local.csv', train_local)
    ]
    
    archivos_guardados = []
    for filename, data in archivos:
        data.to_csv(filename, index=False)
        size_mb = os.path.getsize(filename) / (1024*1024)
        print(f"  ✅ {filename} - {len(data):,} filas ({size_mb:.2f} MB)")
        archivos_guardados.append(filename)
    
    return archivos_guardados

def crear_info_file(train_colab, train_local, target_col):
    """Crear archivo con información de la división"""
    total_samples = len(train_colab) + len(train_local)
    info_content = f"""DIVISIÓN DEL DATASET - COMPETENCIA NEURO-KUP
========================================

Archivo original: {INPUT_FILE}
Target: {target_col}
Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

DISTRIBUCIÓN:
- train_colab.csv:   {len(train_colab):,} muestras
- train_local.csv:   {len(train_local):,} muestras  
- TOTAL:             {total_samples:,} muestras

PORCENTAJES:
- Colab:    {len(train_colab)/total_samples*100:.1f}%
- Local:    {len(train_local)/total_samples*100:.1f}%

CONFIGURACIÓN USADA:
- LOCAL_SIZE: {LOCAL_SIZE} 
- RANDOM_STATE: {RANDOM_STATE}

ESTRATEGIA:
División directa en 2 partes para comparación entre entornos local y Colab.
Eliminado el holdout set para maximizar datos de entrenamiento.
"""
    
    with open('split_info.txt', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("  ✅ split_info.txt - Información de la división")

# ================================
# 🚀 FUNCIÓN PRINCIPAL
# ================================

def main():
    """Función principal del script"""
    print("🎯 DIVISIÓN DE DATASET - COMPETENCIA NEURO-KUP")
    print("="*50)
    
    # 1. Verificar archivo
    if not verificar_archivo(INPUT_FILE):
        return 1
    
    # 2. Cargar datos
    print(f"📁 Cargando {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"✅ Datos cargados: {len(df):,} filas")
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")
        return 1
    
    # 3. Identificar target
    target_col = TARGET_COLUMN
    if target_col is None:
        target_col = encontrar_target_automatico(df)
    
    if target_col not in df.columns:
        print(f"❌ Error: Columna target '{target_col}' no encontrada")
        print(f"Columnas disponibles: {list(df.columns)}")
        return 1
    
    # 4. Mostrar información
    mostrar_info_dataset(df, target_col)
      # 5. Dividir dataset
    train_colab, train_local = dividir_dataset(df, target_col)
      # 6. Verificar distribuciones
    verificar_distribuciones(train_colab, train_local, target_col)
    
    # 7. Guardar archivos
    archivos = guardar_archivos(train_colab, train_local)
    crear_info_file(train_colab, train_local, target_col)
    
    # 8. Resumen final
    print("\n🎉 DIVISIÓN COMPLETADA EXITOSAMENTE")
    print("="*50)
    print(f"📁 Archivos generados ({len(archivos)+1}):")
    for archivo in archivos + ['split_info.txt']:
        print(f"  - {archivo}")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("  1. Sube 'train_colab.csv' a Google Colab")
    print("  2. Usa 'train_local.csv' en tu entorno local")
    print("  3. Compara resultados entre ambos entornos")
    print("="*50)
    
    return 0

# ================================
# 🎮 EJECUCIÓN
# ================================

if __name__ == "__main__":
    # Configuración personalizable desde aquí
    
    # Si quieres cambiar el nombre del archivo o target
    # INPUT_FILE = 'mi_dataset.csv'
    # TARGET_COLUMN = 'mi_target'
    
    exit_code = main()
    sys.exit(exit_code)