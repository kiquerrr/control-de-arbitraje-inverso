# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: main.py
# DESCRIPCION: Script principal para la ejecucion diaria y control historico del arbitraje.
# ==========================================================

import math
import pandas as pd
import os
from datetime import date
from arbitraje_core import CicloArbitraje

# ==========================================================
# --- 1. PARAMETROS DE CONFIGURACION DEL PROYECTO ---
# ==========================================================

# Parametros del ciclo (Configurables)
DIAS_CICLO_DEFAULT = 30
LIMITE_FINAL_USD = 1000.00      
MAX_CICLOS_DIARIOS = 3          

# Parametros Financieros (Base para sugerencias)
COSTO_COMPRA_BASE = 1.04424     
COMISION_P2P_MAKER = 0.0035     
TASA_VENTA_OBJETIVO = 1.12895   

# Parametros de Inversion
PORCENTAJE_AHORRO_BTC = 0.50    

# Archivos y Saldo
ARCHIVO_HISTORICO = 'data/historico_arbitraje.csv' 
ARCHIVO_CONFIG = 'data/config_ciclo.txt'

# --------------------------------------------------------------------------
# --- 2. FUNCIONES DE GESTION DE SALDO Y ESTADO ---
# --------------------------------------------------------------------------

def guardar_estado(saldo: float, dias_ciclo: int, capital_inicial_global: float):
    """Guarda el saldo total y la duracion del ciclo."""
    os.makedirs(os.path.dirname(ARCHIVO_HISTORICO), exist_ok=True)
    with open(ARCHIVO_CONFIG, 'w') as f:
        f.write(f"SALDO:{round(saldo, 2)}\n")
        f.write(f"DIAS:{dias_ciclo}\n")
        f.write(f"C_INICIAL_GLOBAL:{round(capital_inicial_global, 2)}") # Nuevo registro del Capital Global

def cargar_estado():
    """Carga el saldo, la duracion del ciclo y el capital inicial global o pide iniciar."""
    if os.path.exists(ARCHIVO_CONFIG):
        with open(ARCHIVO_CONFIG, 'r') as f:
            lines = f.readlines()
            saldo = float(lines[0].split(':')[1].strip())
            dias = int(lines[1].split(':')[1].strip())
            # Manejo de error si la linea C_INICIAL_GLOBAL no existe aun (migracion)
            try:
                capital_global = float(lines[2].split(':')[1].strip())
            except (IndexError, ValueError):
                capital_global = 0.0
        return saldo, dias, capital_global
    return 0.0, 0, 0.0 # Retorna cero para indicar que es un ciclo nuevo

def calcular_capital_inicial_ajustado(modelo: CicloArbitraje) -> float:
    """Calcula el capital inicial optimo para el Dia 1."""
    try:
        tasa_crecimiento = modelo.get_tasa_rentabilidad_por_ciclo() 
        factor_crecimiento_total = (1 + tasa_crecimiento) ** modelo.DIAS_CICLO
        return modelo.LIMITE_FINAL_USD / factor_crecimiento_total
    except ValueError:
        return 0.0


def calcular_tasa_publicacion_sugerida(tasa_mercado: float, costo_compra: float, comision: float) -> float:
    """Calcula la tasa de venta sugerida basada en el 2% de rentabilidad neta."""
    rentabilidad_objetivo = 0.02
    tasa_publicacion_objetivo = costo_compra * (1 + rentabilidad_objetivo) / (1 - comision)
    
    # Publicar al objetivo a menos que la tasa de mercado sea significativamente menor
    return min(tasa_mercado, tasa_publicacion_objetivo)

def cargar_historial() -> pd.DataFrame:
    """Carga el historial desde CSV o crea un nuevo DataFrame."""
    if os.path.exists(ARCHIVO_HISTORICO):
        return pd.read_csv(ARCHIVO_HISTORICO)
    else:
        return pd.DataFrame(columns=[
            'Dia', 'Fecha', 'C_Inicial_USD', 'Tasa_Venta_P2P', 'Ciclos_Completados', 
            'USDT_Comprado_Total', 'Ganancia_Neta_Diaria', 'C_Final_USD', 
            'Costo_Compra_USD', 'Comision_P2P_Aplicada'
        ])


def guardar_registro(df_historico: pd.DataFrame, nuevo_registro: dict):
    """Anade un nuevo registro y guarda el DataFrame en CSV."""
    os.makedirs(os.path.dirname(ARCHIVO_HISTORICO), exist_ok=True)
    df_actualizado = pd.concat([df_historico, pd.Series(nuevo_registro).to_frame().T], ignore_index=True)
    df_actualizado.to_csv(ARCHIVO_HISTORICO, index=False)
    return df_historico # Devolvemos el original para no depender del concat en el resto del script


def resumen_final(df_historico: pd.DataFrame, saldo_final_boveda: float, dias_ciclo_total: int, capital_inicial_global: float):
    """Genera el resumen final del ciclo, incluyendo el plan de ahorro BTC."""
    
    # La ganancia total REAL es el Saldo_Boveda_Final - Capital_Inicial_Ciclo
    ganancia_neta_total_real = saldo_final_boveda - capital_inicial_global
    
    print("\n" + "=" * 80)
    print("RESUMEN DE CIERRE DE CICLO")
    print("=" * 80)
    print(f"DURACION DEL CICLO: {dias_ciclo_total} Dias")
    print(f"CAPITAL FINAL: ${saldo_final_boveda:,.2f} USD (Limite: ${LIMITE_FINAL_USD:,.2f})")
    print(f"CAPITAL INICIAL USADO: ${capital_inicial_global:,.2f} USD")
    print(f"GANANCIA NETA TOTAL (REAL): ${ganancia_neta_total_real:,.2f} USD")
    print("-" * 80)
    
    # PLAN DE AHORRO BTC
    monto_ahorro_btc = ganancia_neta_total_real * PORCENTAJE_AHORRO_BTC
    monto_utilidad_operativa = saldo_final_boveda - monto_ahorro_btc

    print(f"1. AHORRO EN BITCOIN ({PORCENTAJE_AHORRO_BTC*100:.0f}% de la ganancia): ${monto_ahorro_btc:,.2f} USDT")
    print(f"2. CAPITAL PARA EL PROXIMO CICLO: ${monto_utilidad_operativa:,.2f} USD")
    print("-" * 80)


# --------------------------------------------------------------------------
# --- 3. FUNCION DE EJECUCION DIARIA ---
# --------------------------------------------------------------------------

def ejecutar_dia():
    """Funcion principal que maneja la logica de ejecucion diaria."""
    
    df_historico = cargar_historial()
    saldo_boveda, DIAS_CICLO_ACTUAL, CAPITAL_INICIAL_GLOBAL = cargar_estado()
    
    # 3.1 GESTION DEL CICLO (INICIO O CONTINUACION)
    
    if DIAS_CICLO_ACTUAL == 0:
        # --- INICIO DEL MACRO CICLO (DIA 1) ---
        dia_actual = 1
        print("--- INICIO DE NUEVO CICLO ---")
        while True:
            try:
                dias = int(input("-> 0. Ingrese la duracion total del ciclo (1-90 dias): "))
                if 1 <= dias <= 90:
                    DIAS_CICLO_ACTUAL = dias
                    break
                else:
                    print("Duracion fuera de rango (1-90).")
            except ValueError:
                print("Entrada no valida.")
        saldo_boveda = 0.0 # Saldo empieza en cero
        CAPITAL_INICIAL_GLOBAL = 0.0 # Capital global empieza en cero
    else:
        # --- CONTINUACION DEL MACRO CICLO ---
        ultimo_registro = df_historico.iloc[-1]
        dia_actual = int(ultimo_registro['Dia']) + 1
        
        if dia_actual > DIAS_CICLO_ACTUAL:
            print(f"? EL CICLO HA FINALIZADO (Dia {DIAS_CICLO_ACTUAL}). Ejecute resumen final.")
            return

    # Sugerencias
    costo_compra_sugerido = df_historico.iloc[-1]['Costo_Compra_USD'] if not df_historico.empty else COSTO_COMPRA_BASE
    
    print(f"\nDIA DE OPERACION: {dia_actual} de {DIAS_CICLO_ACTUAL}")
    print(f"SALDO EN BOVEDA (ACUMULADO): ${saldo_boveda:,.2f} USD")
    print("-" * 50)
    
    # 3.2 PASO 1 Y 2: COMPRA DE CAPITAL (TARJETA)
    
    capital_actual = 0.0
    
    # Flujo de capital: Pregunta si quiere usar el saldo acumulado o agregar nuevo
    if saldo_boveda > 0 and dia_actual > 1:
        # Dias > 1: Usar saldo disponible
        print(f"Capital acumulado disponible en Boveda: ${saldo_boveda:,.2f} USD.")
        while True:
            try:
                monto_compra_usd_str = input(f"-> PASO 1: Monto USD a operar hoy (Sugerido {saldo_boveda:,.2f}): ")
                
                if not monto_compra_usd_str:
                    capital_actual = saldo_boveda # Usar todo el saldo por defecto (reinversion total)
                else:
                    capital_actual = float(monto_compra_usd_str)
                    
                if capital_actual <= 0:
                    print("El capital debe ser positivo.")
                elif capital_actual > saldo_boveda:
                    print("? El monto excede el saldo acumulado. Por favor, ingrese un monto menor o igual.")
                else:
                    break
            except ValueError:
                print("Entrada no valida.")
        
        # Si se usa saldo de la Boveda, el costo de compra se asume ya pagado (1.0)
        costo_compra_actual = 1.0 
        
    else:
        # Dia 1 o Boveda en cero: Obligado a inyectar capital fresco
        print("?? Boveda vacia o Dia 1. Debe inyectar capital fresco (Tarjeta).")
        while True:
            try:
                monto_compra_usd = float(input(f"-> PASO 1: Monto USD a COMPRAR hoy (Capital Inicial): "))
                if monto_compra_usd <= 0:
                    print("El capital debe ser positivo.")
                elif monto_compra_usd > LIMITE_FINAL_USD:
                    print(f"Advertencia: El monto excede el limite final ({LIMITE_FINAL_USD}). Continua bajo riesgo.")
                    break
                else:
                    capital_actual = monto_compra_usd
                    break
            except ValueError:
                print("Entrada no valida.")
        
        # Preguntar el costo de la compra ya que es una nueva adquisicion
        while True:
            try:
                costo_compra_actual_str = input(f"-> PASO 2: Costo USDT/Tarjeta (Ej: {costo_compra_sugerido:.4f}): ")
                costo_compra_actual = float(costo_compra_actual_str) if costo_compra_actual_str else costo_compra_sugerido
                break
            except ValueError:
                print("Entrada no valida.")
        
        # REGISTRO CRÍTICO DEL CAPITAL GLOBAL INICIAL (Solo Dia 1)
        if dia_actual == 1:
             CAPITAL_INICIAL_GLOBAL = capital_actual # Registrar el capital base
             saldo_boveda += capital_actual # Agregar el capital al saldo de la bóveda para que pueda ser operado

    # 3.2 AJUSTE DE SALDO DE BOVEDA (Retirar el capital para operar)
    saldo_boveda -= capital_actual # Retirar el capital que se va a operar del saldo disponible
    
    # 3.3 PASO 3: CALCULAR TASA DE VENTA Y PUBLICAR
    
    while True:
        try:
            tasa_p2p_mercado = float(input(f"\n-> PASO 3a: Tasa P2P promedio de Venta (Competencia): "))
            
            # Inicializar simulacion para verificar rentabilidad y sugerir tasa
            simulacion = CicloArbitraje(capital_inicial_usd=capital_actual, 
                                        tasa_venta_p2p_publicada=TASA_VENTA_OBJETIVO, # Placeholder
                                        costo_compra_usdt=costo_compra_actual,
                                        comision_p2p_maker=COMISION_P2P_MAKER,
                                        dias_ciclo=DIAS_CICLO_ACTUAL, limite_final_usd=LIMITE_FINAL_USD,
                                        max_ciclos_diarios=MAX_CICLOS_DIARIOS)
            
            tasa_publicacion_sugerida = calcular_tasa_publicacion_sugerida(
                tasa_p2p_mercado, costo_compra_actual, COMISION_P2P_MAKER
            )
            
            tasa_ingresada = float(input(f"-> PASO 3b: Tasa Real de Venta a publicar (Sugerida {tasa_publicacion_sugerida:.4f}): "))
            
            # Actualizar y verificar
            simulacion.tasa_venta_p2p_publicada = tasa_ingresada
            simulacion._calcular_tasas_derivadas()
            
            rentabilidad_ciclo = simulacion.get_rentabilidad_porcentual_por_ciclo()
            if rentabilidad_ciclo < 0:
                print(f"?? La tasa NO es rentable. Margen: {rentabilidad_ciclo:.3f}%.")
                continue
            
            if rentabilidad_ciclo > 2.0:
                print(f"?? Margen alto ({rentabilidad_ciclo:.2f}%). Cuidado con la competitividad!")

            break
        except ValueError:
            print("Entrada no valida.")
        except Exception as e:
            print(f"Error al calcular: {e}.")


    # 3.4 PASO 4: VENTA Y CALCULO DE GANANCIA
    
    while True:
        try:
            ciclos = int(input(f"\n-> PASO 4: Ciclos Completados (Max {MAX_CICLOS_DIARIOS}): "))
            if 1 <= ciclos <= MAX_CICLOS_DIARIOS:
                break
            else:
                print(f"El numero de ciclos debe estar entre 1 y {MAX_CICLOS_DIARIOS}.")
        except ValueError:
            print("Entrada no valida.")

    # Calculos finales
    ganancia_neta_diaria = simulacion.calcular_ganancia_neta(capital_actual, ciclos_completados=ciclos)
    usdt_total_comprado = simulacion.calcular_usdt_comprado(capital_actual, ciclos_completados=ciclos)
    
    # 3.5 PASO 5: CIERRE Y REINVERSION
    
    capital_final_operacion = capital_actual + ganancia_neta_diaria
    
    # Devolver el monto total de la operacion a la Boveda
    saldo_boveda += capital_final_operacion

    while True:
        decision = input(f"\n-> PASO 5: Desea retirar la ganancia (${ganancia_neta_diaria:,.2f})? (S/N): ").upper()
        if decision == 'N':
            # Reinversion total: Todo queda en la Boveda. No se toca el saldo.
            ganancia_retenida = ganancia_neta_diaria
            print("Reinversion total. Todo el capital y ganancia quedan en la Boveda.")
            break
        elif decision == 'S':
            # Retiro: Se retira la ganancia, dejando solo el capital inicial en la Boveda.
            saldo_boveda -= ganancia_neta_diaria 
            ganancia_retenida = 0.0
            print(f"Retiro de ganancia completado.")
            break
        else:
            print("Opcion no valida.")
            
    # Ajuste para el registro
    if decision == 'S':
        ganancia_neta_diaria = 0.0 
        capital_final_operacion = capital_actual 
    
    # Aplicar el limite (Si estamos en el ultimo dia, el saldo debe ser LIMITE_FINAL_USD)
    if dia_actual == DIAS_CICLO_ACTUAL:
        if saldo_boveda > LIMITE_FINAL_USD:
            exceso = saldo_boveda - LIMITE_FINAL_USD
            
            # Ajuste de ganancia y saldo para el registro final
            if decision == 'N':
                ganancia_neta_diaria -= exceso 
            
            saldo_boveda = LIMITE_FINAL_USD
            capital_final_operacion = LIMITE_FINAL_USD 

            
    # 3.6 REGISTRO
    nuevo_registro = {
        'Dia': dia_actual, 'Fecha': date.today().strftime("%Y-%m-%d"),
        'C_Inicial_USD': round(capital_actual, 2), 'Tasa_Venta_P2P': tasa_ingresada,
        'Ciclos_Completados': ciclos, 'USDT_Comprado_Total': round(usdt_total_comprado, 4),
        'Ganancia_Neta_Diaria': round(ganancia_neta_diaria, 2), 'C_Final_USD': round(capital_final_operacion, 2),
        'Costo_Compra_USD': simulacion.COSTO_COMPRA_TARJETA, 'Comision_P2P_Aplicada': simulacion.COMISION_BINANCE_P2P
    }
    
    guardar_registro(df_historico, nuevo_registro)
    guardar_estado(saldo_boveda, DIAS_CICLO_ACTUAL, CAPITAL_INICIAL_GLOBAL) 
    
    # Reporte
    print("\n--- RESUMEN DEL DIA ---")
    print(f"Ganancia Neta del Dia Registrada: ${ganancia_neta_diaria:,.2f} USD")
    print(f"SALDO DISPONIBLE EN BOVEDA para manana: ${saldo_boveda:,.2f} USD")
    print("-" * 50)


    if dia_actual == DIAS_CICLO_ACTUAL:
        resumen_final(df_historico, saldo_boveda, DIAS_CICLO_ACTUAL, CAPITAL_INICIAL_GLOBAL) 
        # Limpiar archivos de configuracion para proximo ciclo
        os.remove(ARCHIVO_CONFIG)
        
    elif dia_actual < DIAS_CICLO_ACTUAL:
        print(f"Historial guardado. Listo para operar el Dia {dia_actual + 1}.")


if __name__ == "__main__":
    try:
        ejecutar_dia()
    except Exception as e:
        print(f"\n--- ERROR FATAL ---")
        print(f"Ocurrio un error general: {e}")