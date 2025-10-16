# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: reportes.py
# DESCRIPCION: Generador de reportes y analisis
# ==========================================================

import pandas as pd
import os
from utils import imprimir_titulo, imprimir_separador, formatear_moneda, formatear_porcentaje

def generar_reporte_ciclo(archivo_historico: str, capital_inicial_global: float):
    """Genera un reporte completo del ciclo actual"""
    
    if not os.path.exists(archivo_historico):
        print("?? No hay historial disponible para generar reporte.")
        return
    
    df = pd.read_csv(archivo_historico)
    
    if df.empty:
        print("?? El historial está vacío.")
        return
    
    imprimir_titulo("?? REPORTE DETALLADO DEL CICLO")
    
    # Métricas generales
    total_dias = len(df)
    total_ganancia = df['Ganancia_Bruta_Diaria'].sum() if 'Ganancia_Bruta_Diaria' in df.columns else df['Ganancia_Neta_Diaria'].sum()
    total_usdt_operado = df['USDT_Comprado_Total'].sum()
    total_ciclos = df['Ciclos_Completados'].sum()
    
    promedio_ganancia_dia = total_ganancia / total_dias if total_dias > 0 else 0
    promedio_ciclos_dia = total_ciclos / total_dias if total_dias > 0 else 0
    
    # ROI
    capital_final = df.iloc[-1]['C_Final_USD']
    roi_total = ((capital_final - capital_inicial_global) / capital_inicial_global * 100) if capital_inicial_global > 0 else 0
    
    print(f"\n?? MÉTRICAS GENERALES:")
    print(f"   Días Operados:              {total_dias}")
    print(f"   Capital Inicial:            {formatear_moneda(capital_inicial_global)}")
    print(f"   Capital Final:              {formatear_moneda(capital_final)}")
    print(f"   Ganancia Total:             {formatear_moneda(total_ganancia)}")
    print(f"   ROI Total:                  {formatear_porcentaje(roi_total)}")
    
    print(f"\n?? OPERACIONES:")
    print(f"   USDT Total Operado:         {total_usdt_operado:,.2f} USDT")
    print(f"   Ciclos Completados:         {total_ciclos}")
    print(f"   Promedio Ciclos/Día:        {promedio_ciclos_dia:.1f}")
    print(f"   Ganancia Promedio/Día:      {formatear_moneda(promedio_ganancia_dia)}")
    
    # Mejor y peor día
    mejor_dia = df.loc[df['Ganancia_Bruta_Diaria' if 'Ganancia_Bruta_Diaria' in df.columns else 'Ganancia_Neta_Diaria'].idxmax()]
    peor_dia = df.loc[df['Ganancia_Bruta_Diaria' if 'Ganancia_Bruta_Diaria' in df.columns else 'Ganancia_Neta_Diaria'].idxmin()]
    
    print(f"\n?? MEJORES Y PEORES DÍAS:")
    print(f"   Mejor Día:  Día {int(mejor_dia['Dia'])} - {formatear_moneda(mejor_dia['Ganancia_Bruta_Diaria' if 'Ganancia_Bruta_Diaria' in df.columns else 'Ganancia_Neta_Diaria'])}")
    print(f"   Peor Día:   Día {int(peor_dia['Dia'])} - {formatear_moneda(peor_dia['Ganancia_Bruta_Diaria' if 'Ganancia_Bruta_Diaria' in df.columns else 'Ganancia_Neta_Diaria'])}")
    
    # Tasas promedio
    tasa_venta_promedio = df['Tasa_Venta_P2P'].mean()
    tasa_compra_promedio = df['Costo_Compra_USD'].mean()
    spread_promedio = ((tasa_venta_promedio / tasa_compra_promedio) - 1) * 100
    
    print(f"\n?? TASAS PROMEDIO:")
    print(f"   Tasa Compra:    {tasa_compra_promedio:.4f} USD/USDT")
    print(f"   Tasa Venta:     {tasa_venta_promedio:.4f} USD/USDT")
    print(f"   Spread Promedio: {formatear_porcentaje(spread_promedio)}")
    
    imprimir_separador()

def mostrar_ultimos_dias(archivo_historico: str, n_dias: int = 5):
    """Muestra los últimos N días de operaciones"""
    
    if not os.path.exists(archivo_historico):
        print("?? No hay historial disponible.")
        return
    
    df = pd.read_csv(archivo_historico)
    
    if df.empty:
        print("?? El historial está vacío.")
        return
    
    ultimos = df.tail(n_dias)
    
    imprimir_titulo(f"?? ÚLTIMOS {min(n_dias, len(ultimos))} DÍAS DE OPERACIONES")
    
    print(f"\n{'Día':<5} {'Fecha':<12} {'Capital':<12} {'Ciclos':<7} {'Ganancia':<12} {'ROI%':<8}")
    imprimir_separador("-", 80)
    
    for _, row in ultimos.iterrows():
        ganancia = row['Ganancia_Bruta_Diaria'] if 'Ganancia_Bruta_Diaria' in row else row['Ganancia_Neta_Diaria']
        roi = (ganancia / row['C_Inicial_USD'] * 100) if row['C_Inicial_USD'] > 0 else 0
        
        print(f"{int(row['Dia']):<5} {row['Fecha']:<12} {formatear_moneda(row['C_Inicial_USD']):<12} "
              f"{int(row['Ciclos_Completados']):<7} {formatear_moneda(ganancia):<12} {roi:>6.2f}%")
    
    imprimir_separador()

def exportar_reporte_txt(archivo_historico: str, capital_inicial_global: float, output_file: str = 'data/reporte_ciclo.txt'):
    """Exporta el reporte completo a un archivo de texto"""
    
    if not os.path.exists(archivo_historico):
        print("?? No hay historial para exportar.")
        return
    
    df = pd.read_csv(archivo_historico)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("REPORTE DE ARBITRAJE P2P - CICLO COMPLETO\n")
        f.write(f"Generado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        total_ganancia = df['Ganancia_Bruta_Diaria'].sum() if 'Ganancia_Bruta_Diaria' in df.columns else df['Ganancia_Neta_Diaria'].sum()
        capital_final = df.iloc[-1]['C_Final_USD']
        roi_total = ((capital_final - capital_inicial_global) / capital_inicial_global * 100) if capital_inicial_global > 0 else 0
        
        f.write("RESUMEN EJECUTIVO\n")
        f.write("-"*80 + "\n")
        f.write(f"Capital Inicial:     {formatear_moneda(capital_inicial_global)}\n")
        f.write(f"Capital Final:       {formatear_moneda(capital_final)}\n")
        f.write(f"Ganancia Total:      {formatear_moneda(total_ganancia)}\n")
        f.write(f"ROI Total:           {formatear_porcentaje(roi_total)}\n")
        f.write(f"Días Operados:       {len(df)}\n\n")
        
        f.write("DETALLE DIARIO\n")
        f.write("-"*80 + "\n")
        f.write(df.to_string(index=False))
    
    print(f"? Reporte exportado a: {output_file}")