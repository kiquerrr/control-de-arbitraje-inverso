# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: main.py
# VERSION: 3.0 - Con BD SQLite y ventas individuales (CORREGIDO Y LIMPIO)
# ==========================================================

import warnings
import os
from datetime import date
from database import ArbitrajeDB
from utils import (validar_numero_positivo, validar_entero_rango, 
                   confirmar_accion, formatear_moneda, formatear_porcentaje,
                   imprimir_titulo, imprimir_separador)

warnings.filterwarnings('ignore', category=FutureWarning)

# PARAMETROS GLOBALES (se cargan de la BD)
MAX_VENTAS_DIARIAS = 3
COMISION_P2P_MAKER = 0.0035
LIMITE_FINAL_USD = 1000.00
PORCENTAJE_AHORRO_BTC = 0.50
COSTO_COMPRA_BASE = 1.04424

# Usuario por defecto (multi-usuario para el futuro)
USUARIO_ID = 1

def cargar_parametros_desde_bd(db):
    """Carga parametros del sistema desde la BD"""
    global MAX_VENTAS_DIARIAS, COMISION_P2P_MAKER, LIMITE_FINAL_USD, PORCENTAJE_AHORRO_BTC
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT nombre, valor FROM parametros_sistema")
    params = cursor.fetchall()
    
    for param in params:
        if param['nombre'] == 'MAX_VENTAS_DIARIAS':
            MAX_VENTAS_DIARIAS = int(param['valor'])
        elif param['nombre'] == 'COMISION_P2P_MAKER':
            COMISION_P2P_MAKER = float(param['valor'])
        elif param['nombre'] == 'LIMITE_FINAL_USD':
            LIMITE_FINAL_USD = float(param['valor'])
        elif param['nombre'] == 'PORCENTAJE_AHORRO_BTC':
            PORCENTAJE_AHORRO_BTC = float(param['valor'])

def calcular_venta_individual(monto_venta, tasa_venta_p2p, tasa_compra, comision):
    """Calcula el resultado de UNA venta individual"""
    # monto_venta es el costo en USD de los USDT operados en esta venta
    usdt_operado = monto_venta / tasa_compra
    ingreso_bruto = usdt_operado * tasa_venta_p2p
    comision_monto = ingreso_bruto * comision
    ingreso_neto = ingreso_bruto - comision_monto
    ganancia_venta = ingreso_neto - monto_venta
    
    return {
        'usdt_operado': usdt_operado,
        'ingreso_bruto': ingreso_bruto,
        'comision_monto': comision_monto,
        'ingreso_neto': ingreso_neto,
        'ganancia_venta': ganancia_venta
    }

def solicitar_ventas_del_dia(capital_disponible, max_ventas):
    """Solicita el monto de cada venta individual del dia"""
    ventas = []
    capital_restante = capital_disponible # En USD
    
    print(f"\n{'='*60}")
    print(f"REGISTRO DE VENTAS DEL DIA")
    print(f"Capital disponible para operar: {formatear_moneda(capital_disponible)}")
    print(f"{'='*60}")
    
    num_ventas = validar_entero_rango(
        f"\nCuantas ventas completaste HOY? (Max {max_ventas}): ",
        1, max_ventas
    )
    
    print(f"\nAhora ingresa el MONTO de cada venta:")
    print(f"(La suma no puede exceder {formatear_moneda(capital_disponible)})\n")
    
    for i in range(1, num_ventas + 1):
        # Si ya no queda capital, salir del loop
        if capital_restante < 0.01:
            print(f"\n[OK] Capital agotado. Total de ventas registradas: {len(ventas)}")
            break
        
        while True:
            monto = validar_numero_positivo(
                f"  Venta #{i} - Monto operado: $",
                maximo=capital_restante
            )
            
            if monto > capital_restante:
                print(f"  [ERROR] Error: Solo quedan {formatear_moneda(capital_restante)} disponibles")
                continue
            
            ventas.append(monto)
            capital_restante -= monto
            
            if capital_restante < 0.01:
                print(f"  [OK] Registrada. Capital AGOTADO\n")
            else:
                print(f"  [OK] Registrada. Restante: {formatear_moneda(capital_restante)}\n")
            break
    
    # Solo preguntar si queda más de 1 centavo
    if capital_restante > 0.01:
        usar_resto = confirmar_accion(
            f"\nQuedan {formatear_moneda(capital_restante)} sin operar. Agregar como venta adicional?"
        )
        if usar_resto:
            ventas.append(capital_restante)
    
    return ventas

def preview_ventas(ventas_montos, tasa_venta_p2p, tasa_compra, comision):
    """Muestra preview de todas las ventas del dia"""
    imprimir_titulo("PREVIEW DE VENTAS DEL DIA", "=")
    
    print(f"\n{'Venta':<8} {'Monto':<12} {'USDT':<12} {'Ingreso':<12} {'Comision':<12} {'Ganancia':<12}")
    imprimir_separador("-", 80)
    
    total_monto = 0
    total_usdt = 0
    total_ingreso = 0
    total_comision = 0
    total_ganancia = 0
    
    for i, monto in enumerate(ventas_montos, 1):
        resultado = calcular_venta_individual(monto, tasa_venta_p2p, tasa_compra, comision)
        
        print(f"#{i:<7} {formatear_moneda(monto):<12} "
              f"{resultado['usdt_operado']:>10.2f} "
              f"{formatear_moneda(resultado['ingreso_bruto']):<12} "
              f"{formatear_moneda(resultado['comision_monto']):<12} "
              f"{formatear_moneda(resultado['ganancia_venta']):<12}")
        
        total_monto += monto
        total_usdt += resultado['usdt_operado']
        total_ingreso += resultado['ingreso_bruto']
        total_comision += resultado['comision_monto']
        total_ganancia += resultado['ganancia_venta']
    
    imprimir_separador("-", 80)
    print(f"{'TOTAL':<8} {formatear_moneda(total_monto):<12} "
          f"{total_usdt:>10.2f} "
          f"{formatear_moneda(total_ingreso):<12} "
          f"{formatear_moneda(total_comision):<12} "
          f"{formatear_moneda(total_ganancia):<12}")
    
    print(f"\n[RESUMEN DEL DIA]:")
    print(f"   Capital operado total: {formatear_moneda(total_monto)}")
    print(f"   USDT total operado:    {total_usdt:.2f} USDT")
    print(f"   Ganancia neta dia:     {formatear_moneda(total_ganancia)}")
    print(f"   ROI del dia:           {formatear_porcentaje((total_ganancia/total_monto)*100)}")
    
    imprimir_separador("=", 80)
    
    return {
        'total_monto': total_monto,
        'total_usdt': total_usdt,
        'total_ingreso': total_ingreso,
        'total_comision': total_comision,
        'total_ganancia': total_ganancia
    }

def resumen_final_ciclo(db, ciclo_id):
    """Genera resumen final del ciclo desde la BD"""
    cursor = db.conn.cursor()
    
    # Obtener datos del ciclo
    cursor.execute("SELECT * FROM ciclos WHERE id = ?", (ciclo_id,))
    ciclo = dict(cursor.fetchone())
    
    # Estadisticas de dias
    cursor.execute("""
        SELECT 
            COUNT(*) as total_dias,
            COALESCE(SUM(ganancia_bruta_dia), 0) as ganancia_total,
            COALESCE(SUM(capital_fresco_inyectado), 0) as total_inyectado
        FROM dias WHERE ciclo_id = ?
    """, (ciclo_id,))
    stats = dict(cursor.fetchone())
    
    # Estadisticas de ventas
    cursor.execute("""
        SELECT 
            COUNT(*) as total_ventas,
            COALESCE(SUM(usdt_operado), 0) as total_usdt,
            COALESCE(SUM(comision_monto), 0) as total_comisiones
        FROM ventas v
        JOIN dias d ON v.dia_id = d.id
        WHERE d.ciclo_id = ?
    """, (ciclo_id,))
    stats_ventas = dict(cursor.fetchone())
    
    # Obtener capital final del ultimo dia
    cursor.execute("""
        SELECT saldo_boveda_final, tasa_costo_final 
        FROM dias 
        WHERE ciclo_id = ? 
        ORDER BY dia_numero DESC 
        LIMIT 1
    """, (ciclo_id,))
    ultimo_saldo_row = cursor.fetchone()
    
    capital_inicial = ciclo['capital_inicial']
    
    # El capital final debe ser el valor USD (costo) del USDT en bóveda
    if ultimo_saldo_row:
        saldo_usdt = ultimo_saldo_row['saldo_boveda_final']
        tasa_costo = ultimo_saldo_row['tasa_costo_final']
        capital_final = saldo_usdt * tasa_costo
    else:
        capital_final = capital_inicial
    
    capital_final = ciclo['capital_final'] if ciclo['capital_final'] else capital_final
    
    ganancia_total = capital_final - capital_inicial
    roi_total = (ganancia_total / capital_inicial * 100) if capital_inicial > 0 else 0
    
    imprimir_titulo("RESUMEN FINAL DEL CICLO")
    
    print(f"\n[CICLO]: {ciclo['nombre_ciclo']}")
    print(f"   Duracion: {ciclo['dias_totales']} dias ({stats['total_dias']} completados)")
    print(f"   Fecha inicio: {ciclo['fecha_inicio']}")
    print(f"   Fecha fin: {ciclo['fecha_fin']}")
    
    print(f"\n[RESULTADOS FINANCIEROS]:")
    print(f"   Capital inicial:  {formatear_moneda(capital_inicial)}")
    print(f"   Capital final:    {formatear_moneda(capital_final)}")
    print(f"   Ganancia total:   {formatear_moneda(ganancia_total)}")
    print(f"   ROI total:        {formatear_porcentaje(roi_total)}")
    
    if ciclo['dias_totales'] > 0:
        # Usamos el capital_final en USD para el cálculo
        roi_diario = ((capital_final / capital_inicial) ** (1/ciclo['dias_totales']) - 1) * 100
        print(f"   ROI diario (compuesto): {formatear_porcentaje(roi_diario, 3)}")
    
    print(f"\n[OPERACIONES]:")
    print(f"   Total ventas:     {stats_ventas['total_ventas']}")
    print(f"   USDT operado:     {stats_ventas['total_usdt']:.2f} USDT")
    print(f"   Comisiones:       {formatear_moneda(stats_ventas['total_comisiones'])}")
    
    # Plan de ahorro BTC
    monto_btc = ganancia_total * PORCENTAJE_AHORRO_BTC
    monto_proximo = capital_final - monto_btc
    
    print(f"\n[PLAN DE AHORRO]:")
    print(f"   Para BTC ({PORCENTAJE_AHORRO_BTC*100:.0f}%):  {formatear_moneda(monto_btc)}")
    print(f"   Proximo ciclo:    {formatear_moneda(monto_proximo)}")
    
    imprimir_separador()


def cerrar_dia(capital_operado_usd, usdt_operados, tasa_venta, comision):
    """
    Al cerrar el dia, pregunta que paso realmente con los USDT
    """
    print("\n" + "="*60)
    print("CIERRE DEL DIA - Que hiciste con los USDT?")
    print("="*60)
    
    print(f"\n[Resumen de tu operacion]:")
    print(f"   Capital operado:  {formatear_moneda(capital_operado_usd)}")
    print(f"   USDT en juego:    {usdt_operados:.4f} USDT")
    
    # Calcular ganancia potencial si vendio todo
    ingreso_total = usdt_operados * tasa_venta * (1 - comision)
    ganancia_total = ingreso_total - capital_operado_usd
    
    print(f"   Si vendes todo:   {formatear_moneda(ingreso_total)}")
    print(f"   Ganancia seria:   {formatear_moneda(ganancia_total)}")
    
    print("\nQue paso REALMENTE con esos USDT?")
    print("  1. Vendi TODO (fue a mi banco/tarjeta)")
    print("  2. Vendi PARTE (parte a banco, resto en Binance)")
    print("  3. NO vendi NADA (todo queda en USDT en Binance)")
    
    opcion = validar_entero_rango("\nOpcion (1-3): ", 1, 3)
    
    if opcion == 1:
        # VENDIO TODO
        usd_a_banco = ingreso_total
        usdt_en_boveda = 0
        ganancia_real = ganancia_total
        
        print(f"\n[Operacion completa]:")
        print(f"   A tu banco:       {formatear_moneda(usd_a_banco)}")
        print(f"   Ganancia real:    {formatear_moneda(ganancia_real)}")
        print(f"   USDT en Binance:  0 USDT")
        print(f"\n   [AVISO] Manana debes COMPRAR USDT de nuevo")
        
    elif opcion == 2:
        # VENDIO PARTE
        print(f"\n[De los {usdt_operados:.4f} USDT disponibles]:")
        
        usdt_vendidos = validar_numero_positivo(
            f"Cuantos USDT VENDISTE? (Max {usdt_operados:.4f}): ",
            maximo=usdt_operados
        )
        
        usdt_en_boveda = usdt_operados - usdt_vendidos
        usd_a_banco = usdt_vendidos * tasa_venta * (1 - comision)
        costo_usdt_vendidos = (usdt_vendidos / usdt_operados) * capital_operado_usd
        ganancia_real = usd_a_banco - costo_usdt_vendidos
        
        print(f"\n[Operacion parcial]:")
        print(f"   A tu banco:       {formatear_moneda(usd_a_banco)}")
        print(f"   Ganancia real:    {formatear_moneda(ganancia_real)}")
        print(f"   USDT en Binance:  {usdt_en_boveda:.4f} USDT")
        print(f"\n   [INFO] Manana puedes operar esos {usdt_en_boveda:.4f} USDT")
        
    else:
        # NO VENDIO NADA
        usdt_en_boveda = usdt_operados
        usd_a_banco = 0
        ganancia_real = 0
        
        print(f"\n[USDT retenidos]:")
        print(f"   A tu banco:       $0.00 USD")
        print(f"   Ganancia real:    $0.00 (aun no vendiste)")
        print(f"   USDT en Binance:  {usdt_en_boveda:.4f} USDT")
        print(f"\n   [INFO] Manana operas con esos {usdt_en_boveda:.4f} USDT")
    
    return {
        'usd_a_banco': usd_a_banco,
        'usdt_en_boveda': usdt_en_boveda,
        'ganancia_real': ganancia_real,
        'opcion': opcion
    }


def ejecutar_dia():
    """Funcion principal de ejecucion diaria con BD"""
    
    db = ArbitrajeDB()
    cargar_parametros_desde_bd(db)
    
    # Verificar si hay ciclo activo
    ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
    
    if not ciclo:
        # INICIAR NUEVO CICLO
        imprimir_titulo("INICIO DE NUEVO CICLO")
        
        dias_totales = validar_entero_rango(
            "-> Duracion del ciclo (1-90 dias): ", 1, 90
        )
        
        print("\n[CAPITAL INICIAL DEL CICLO]")
        print("="*60)
        print("\n[IMPORTANTE]: Elige como iniciaras este ciclo:")
        print("\n  A) Comprare USDT AHORA con USD de mi tarjeta/banco")
        print("  B) Ya TENGO USDT (de ciclos anteriores o wallet)\n")
        print("="*60)
        
        tipo_capital = input("\nTu opcion [A/B]: ").strip().upper()
        
        if tipo_capital == 'A':
            # ===== OPCIÓN A: COMPRAR USDT AHORA =====
            print("\n" + "="*60)
            print("COMPRA DE USDT - PASO A PASO")
            print("="*60)
            
            # PASO 1: Monto en USD que gastará
            print("\n[PASO 1]: Cuantos USD vas a GASTAR?")
            print("  (Es el dinero que saldra de tu tarjeta/banco)\n")
            
            monto_usd_gastar = validar_numero_positivo(
                "-> Monto USD a gastar: $",
                maximo=10000
            )
            
            # PASO 2: Tasa de compra de Binance
            print("\n" + "-"*60)
            print("[PASO 2]: A que TASA compraras los USDT?")
            print("  (Ve a Binance > Comprar Crypto > USDT)")
            print("  Ejemplo: Si dice '1 USDT = $1.0442', ingresa 1.0442\n")
            
            while True:
                tasa_compra_inicial = validar_numero_positivo(
                    f"-> Tasa de compra Binance (Sugerida {COSTO_COMPRA_BASE:.4f}): $",
                    default=COSTO_COMPRA_BASE
                )
                
                # Validar que la tasa sea razonable (entre 0.95 y 1.15)
                if 0.95 <= tasa_compra_inicial <= 1.15:
                    break
                else:
                    print(f"\n[AVISO] Tasa fuera de rango normal (0.95 - 1.15)")
                    if confirmar_accion("Reintentar?"):
                        continue
                    else:
                        break
            
            # PASO 3: Calcular USDT que recibirá
            usdt_equivalente = monto_usd_gastar / tasa_compra_inicial
            
            print("\n" + "="*60)
            print("[CONFIRMACION DE COMPRA]")
            print("="*60)
            print(f"\nGastaras:        {formatear_moneda(monto_usd_gastar)} USD")
            print(f"Tasa Binance:    {tasa_compra_inicial:.4f} USD/USDT")
            print(f"Recibiras:       {usdt_equivalente:.4f} USDT")
            print(f"Costo por USDT:  {tasa_compra_inicial:.4f} USD/USDT")
            print("\n" + "="*60)
            
            if not confirmar_accion("\nConfirmar estos datos?"):
                print("\n[CANCELADO] Inicio de ciclo cancelado")
                db.cerrar()
                return
            
            capital_inicial = monto_usd_gastar
            
        else:
            # ===== OPCIÓN B: YA TIENE USDT =====
            print("\n" + "="*60)
            print("USDT EXISTENTE")
            print("="*60)
            print("\nIngresa la cantidad de USDT que ya tienes")
            print("  (Estos USDT ya estan en tu wallet/cuenta)\n")
            
            usdt_equivalente = validar_numero_positivo(
                "-> Cantidad de USDT disponibles: ",
                maximo=100000
            )
            
            capital_inicial = usdt_equivalente  # Equivalencia 1:1 para fines de reporte
            tasa_compra_inicial = 1.0
            
            print(f"\n[OK] Iniciando con {usdt_equivalente:.4f} USDT")
            print(f"  (Equivalente a ~{formatear_moneda(capital_inicial)} USD)")
        
        nombre_ciclo = input("\n-> Nombre del ciclo (Enter para auto): ").strip()
        
        ciclo_id = db.iniciar_ciclo(
            usuario_id=USUARIO_ID,
            dias_totales=dias_totales,
            capital_inicial=capital_inicial,
            nombre_ciclo=nombre_ciclo if nombre_ciclo else None,
            tasa_compra_inicial=tasa_compra_inicial,
            tipo_capital='USD_FRESCO' if tipo_capital == 'A' else 'USDT_EXISTENTE'
        )
        
        ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
        
        # CRÍTICO: La bóveda guarda USDT, no USD
        saldo_boveda = usdt_equivalente
        # NUEVO: Guardar la tasa de costo inicial como tasa de costo de bóveda
        tasa_costo_boveda = tasa_compra_inicial
        
        print(f"\n[BOVEDA INICIAL]:")
        print(f"   Capital invertido: {formatear_moneda(capital_inicial)} USD")
        print(f"   USDT en boveda:    {saldo_boveda:.4f} USDT")
        print(f"   Tasa de costo:     {tasa_costo_boveda:.4f} USD/USDT")
        
        dia_actual = 1
        
        print(f"\n[OK] Ciclo iniciado: {ciclo['nombre_ciclo']}")
        print(f"   ID: {ciclo_id}")
        print(f"   Capital inicial: {formatear_moneda(capital_inicial)}")
        
    else:
        # CONTINUAR CICLO EXISTENTE
        ciclo_id = ciclo['id']
        ultimo_dia = db.obtener_ultimo_dia(ciclo_id)
        
        if ultimo_dia:
            dia_actual = ultimo_dia['dia_numero'] + 1
            saldo_boveda = ultimo_dia['saldo_boveda_final']
            # CORRECCIÓN 1: OBTENER TASA DE COSTO DE LA BOVEDA DEL DÍA ANTERIOR
            tasa_costo_boveda = ultimo_dia['tasa_costo_final'] 
        else:
            dia_actual = 1
            saldo_boveda = ciclo['capital_inicial']
            # Obtener tasa_compra_inicial del ciclo
            tasa_costo_boveda = ciclo['tasa_compra_inicial']

        # Verificar si el ciclo ya termino
        if dia_actual > ciclo['dias_totales']:
            print(f"\n[OK] CICLO FINALIZADO")
            resumen_final_ciclo(db, ciclo_id)
            
            if confirmar_accion("\nIniciar nuevo ciclo?"):
                # Se pasa el capital final en USD (costo) para el registro
                capital_final_usd = saldo_boveda * tasa_costo_boveda
                
                db.finalizar_ciclo(
                    ciclo_id=ciclo_id,
                    capital_final=capital_final_usd,
                    ganancia_total=capital_final_usd - ciclo['capital_inicial'],
                    roi_total=((capital_final_usd - ciclo['capital_inicial']) / ciclo['capital_inicial']) * 100
                )
                db.cerrar()
                # Reiniciar
                return ejecutar_dia()
            else:
                db.cerrar()
                return
    
    # OPERACION DEL DIA
    imprimir_separador()
    print(f"\n{'='*60}")
    print(f"DIA {dia_actual} de {ciclo['dias_totales']} - {ciclo['nombre_ciclo']}")
    # Mostrar saldo en USD (solo para fines de presentación)
    print(f"SALDO EN BOVEDA: {formatear_moneda(saldo_boveda * tasa_costo_boveda)} ({saldo_boveda:.4f} USDT)") 
    print(f"TASA COSTO BOVEDA: {tasa_costo_boveda:.4f} USD/USDT") # NUEVO: Mostrar tasa de costo actual
    print(f"{'='*60}")
    
    # PASO 1: DECISION DE CAPITAL A OPERAR
    capital_disponible_inicio = saldo_boveda # USDT
    capital_operado = 0.0 # USDT a operar
    capital_no_operado = 0.0 # USDT que quedan en bóveda
    capital_fresco = 0.0 # USD gastado en capital fresco
    tipo_operacion = ""
    tasa_compra_promedio = tasa_costo_boveda # Costo del capital a operar
    
    if saldo_boveda > 0 and dia_actual > 1:
        # HAY SALDO
        print(f"\n[OPCIONES DE CAPITAL]:")
        print("   1. Operar TODO el saldo")
        print("   2. Operar PARTE del saldo")
        print("   3. Solo inyectar capital FRESCO")
        print("   4. Operar PARTE + capital FRESCO")
        
        opcion = input("\nOpcion (1-4): ").strip()
        
        if opcion == "1":
            capital_operado = saldo_boveda
            capital_no_operado = 0.0
            tasa_compra_promedio = tasa_costo_boveda # CORRECTO: Usa el costo de la bóveda
            tipo_operacion = "REINVERSION_TOTAL"
            
        elif opcion == "2":
            # Monto a operar en USDT
            capital_operado = validar_numero_positivo(
                f"Monto a operar (Max {formatear_moneda(saldo_boveda * tasa_costo_boveda)}): $", # Mostrar en USD
                maximo=saldo_boveda
            )
            capital_no_operado = saldo_boveda - capital_operado
            tasa_compra_promedio = tasa_costo_boveda # CORRECTO: Usa el costo de la bóveda
            tipo_operacion = "REINVERSION_PARCIAL"
            
        elif opcion == "3":
            # NO operar bóveda, solo capital fresco
            capital_no_operado = saldo_boveda  # USDT que quedan en bóveda
            
            print("\n[COMPRA DE CAPITAL FRESCO]")
            monto_usd_fresco = validar_numero_positivo("Monto USD a gastar (tarjeta): $")
            
            tasa_compra_fresco = validar_numero_positivo(
                f"Tasa de compra Binance (Sugerida {COSTO_COMPRA_BASE:.4f}): $",
                default=COSTO_COMPRA_BASE
            )
            
            # Calcular USDT que recibirá
            usdt_fresco = monto_usd_fresco / tasa_compra_fresco
            
            print(f"\nGastaras:     {formatear_moneda(monto_usd_fresco)} USD")
            print(f"Recibiras:    {usdt_fresco:.4f} USDT")
            print(f"En boveda:    {saldo_boveda:.4f} USDT (sin tocar)")
            
            capital_operado = usdt_fresco  # ? USDT OPERADOS
            capital_fresco = monto_usd_fresco  # USD gastado (para registro)
            tasa_compra_promedio = tasa_compra_fresco
            tipo_operacion = "CAPITAL_FRESCO_PURO"
            
        elif opcion == "4":
            # Opción 4: Parte de bóveda + capital fresco
            print(f"\n[Boveda disponible]: {saldo_boveda:.4f} USDT")
            
            usdt_de_boveda = validar_numero_positivo(
                f"Cuantos USDT operar de boveda? (Max {saldo_boveda:.4f}): ",
                maximo=saldo_boveda
            )
            
            print("\n[CAPITAL FRESCO ADICIONAL]")
            monto_usd_fresco = validar_numero_positivo("Monto USD a gastar (tarjeta): $")
            
            tasa_compra_fresco = validar_numero_positivo(
                f"Tasa de compra Binance (Sugerida {COSTO_COMPRA_BASE:.4f}): $",
                default=COSTO_COMPRA_BASE
            )
            
            # Calcular USDT del fresco
            usdt_fresco = monto_usd_fresco / tasa_compra_fresco
            
            # Total a operar en USDT
            capital_operado = usdt_de_boveda + usdt_fresco
            capital_no_operado = saldo_boveda - usdt_de_boveda
            capital_fresco = monto_usd_fresco
            
            # Costo ponderado (CORRECCIÓN 3)
            # 1. Costo real de los USDT operados de la bóveda
            costo_usdt_boveda_operados = usdt_de_boveda * tasa_costo_boveda 
            costo_fresco_usd = monto_usd_fresco
            # 2. Tasa promedio: (Costo Total en USD) / (Total de USDT operados)
            tasa_compra_promedio = (costo_usdt_boveda_operados + costo_fresco_usd) / capital_operado
            
            tipo_operacion = "REINVERSION_MIXTA"
            
            print(f"\n[RESUMEN]:")
            print(f"   USDT boveda:     {usdt_de_boveda:.4f} USDT")
            print(f"   USDT fresco:     {usdt_fresco:.4f} USDT")
            print(f"   -----------------------------")
            print(f"   Total a operar:  {capital_operado:.4f} USDT")
            print(f"   Costo ponderado: {tasa_compra_promedio:.4f} USD/USDT")
            print(f"   USDT en reposo:  {capital_no_operado:.4f} USDT")
        else:
            print("Opcion invalida")
            db.cerrar()
            return
    else:
        # DÍA 1
        if saldo_boveda > 0:
            # Si hay saldo del ciclo anterior
            print(f"\n[Hay saldo en boveda]: {formatear_moneda(saldo_boveda)}")
            usar_saldo = confirmar_accion("Usar este saldo para operar?")
            
            if usar_saldo:
                capital_operado = saldo_boveda
                capital_no_operado = 0.0
                tasa_compra_promedio = tasa_costo_boveda
                tipo_operacion = "SALDO_ANTERIOR"
            else:
                # Quiere inyectar capital fresco (USDT de bóveda no operados)
                capital_no_operado = saldo_boveda
                capital_fresco = validar_numero_positivo("Monto FRESCO a comprar: $")
                capital_operado = capital_fresco / COSTO_COMPRA_BASE # Asumimos se opera todo el USDT comprado
                tasa_compra_promedio = validar_numero_positivo(
                    f"Costo USDT/Tarjeta (Sugerido {COSTO_COMPRA_BASE:.4f}): $",
                    default=COSTO_COMPRA_BASE
                )
                tipo_operacion = "CAPITAL_FRESCO_DIA1"
        else:
            # No hay saldo, obligado a inyectar
            print(f"\n[CAPITAL INICIAL REQUERIDO]")
            capital_fresco = validar_numero_positivo("Monto a COMPRAR (tarjeta): $")
            capital_operado = capital_fresco / COSTO_COMPRA_BASE # Asumimos se opera todo el USDT comprado
            tasa_compra_promedio = validar_numero_positivo(
                f"Costo USDT/Tarjeta (Sugerido {COSTO_COMPRA_BASE:.4f}): $",
                default=COSTO_COMPRA_BASE
            )
            tipo_operacion = "CAPITAL_INICIAL"
    
    # CRÍTICO: El capital operado (USDT) se retira de la bóveda
    saldo_boveda -= capital_operado
    
    print(f"\n[Movimiento de boveda]:")
    print(f"   Saldo anterior:  {saldo_boveda + capital_operado:.4f} USDT")
    print(f"   Retirando:       {capital_operado:.4f} USDT")
    print(f"   Saldo actual:    {saldo_boveda:.4f} USDT")
    
    # PASO 2: TASA DE VENTA P2P
    # ... (código de análisis de rentabilidad se mantiene igual) ...

    print(f"\n[CONFIGURACION DE VENTA P2P]")
    print("\n[IMPORTANTE]: Consulta la tasa promedio en:")
    print("   Binance P2P > Vender USDT > Ver anuncios de VENTA")
    print("   (Mira las tasas a las que otros VENDEN USDT)\n")
    
    tasa_p2p_mercado = validar_numero_positivo(
        "Tasa promedio del mercado P2P BINANCE de hoy: $"
    )
    
    # Calcular punto de equilibrio
    punto_equilibrio = tasa_compra_promedio / (1 - COMISION_P2P_MAKER)
    
    print(f"\n[ANALISIS DE RENTABILIDAD]:")
    print(f"   Costo de compra:      {tasa_compra_promedio:.4f} USD/USDT")
    print(f"   Punto de equilibrio:  {punto_equilibrio:.4f} USD/USDT")
    print(f"   Tasa mercado:         {tasa_p2p_mercado:.4f} USD/USDT")
    
    # Calcular tasa sugerida (2% de margen sobre punto equilibrio)
    tasa_sugerida = punto_equilibrio * 1.02
    
    # Ajustar si es mayor que el mercado
    if tasa_sugerida > tasa_p2p_mercado:
        tasa_sugerida = tasa_p2p_mercado * 0.995  # 0.5% por debajo del mercado
    
    print(f"   Tasa sugerida:        {tasa_sugerida:.4f} USD/USDT (competitiva y rentable)")
    
    while True:
        tasa_venta_publicada = validar_numero_positivo(
            f"\nTu tasa a publicar (Sugerida {tasa_sugerida:.4f}): $",
            default=tasa_sugerida
        )
        
        # Validar que no esté por debajo del punto de equilibrio
        if tasa_venta_publicada < punto_equilibrio:
            print(f"\n[ERROR]: Tasa por DEBAJO del punto de equilibrio!")
            # ... (código de error)
            if not confirmar_accion("Reintentar con otra tasa?"):
                # Se deshace el retiro de capital de la bóveda si cancela
                saldo_boveda += capital_operado 
                db.cerrar()
                return
            continue
        
        # Calcular margen
        tasa_neta = tasa_venta_publicada * (1 - COMISION_P2P_MAKER)
        margen = ((tasa_neta / tasa_compra_promedio) - 1) * 100
        
        if margen <= 0:
            print(f"\n[ERROR] Tasa NO rentable (Margen: {margen:.2f}%)")
            continue
        
        if margen < 0.5:
            print(f"\n[AVISO] ADVERTENCIA: Margen muy bajo ({formatear_porcentaje(margen)})")
            if not confirmar_accion("Continuar con este margen?"):
                continue
        
        print(f"\n[OK] Tasa rentable. Margen neto: {formatear_porcentaje(margen)}")
        break
    
    # PASO 3: REGISTRAR VENTAS DEL DIA
    # Monto en USD que se está operando (costo ponderado * USDT operados)
    capital_operado_usd_costo = capital_operado * tasa_compra_promedio 
    
    ventas_montos = solicitar_ventas_del_dia(capital_operado_usd_costo, MAX_VENTAS_DIARIAS)
    
    # PREVIEW
    preview_totales = preview_ventas(
        ventas_montos, 
        tasa_venta_publicada, 
        tasa_compra_promedio, 
        COMISION_P2P_MAKER
    )
    
    if not confirmar_accion("\nConfirmar operacion del dia?"):
        print("\n[CANCELADO] Operacion cancelada")
        saldo_boveda += capital_operado
        db.cerrar()
        return
    
    # REGISTRAR EN BD
    ganancia_bruta_dia = preview_totales['total_ganancia']
    
    # Devolver a boveda (USDT)
    # Se devuelve el capital operado (en USDT) más los USDT equivalentes de la ganancia
    usdt_ganancia_equivalente = ganancia_bruta_dia / tasa_compra_promedio # Aproximación
    
    # Saldo boveda se incrementa con los USDT (capital_operado + ganancia_bruta)
    saldo_boveda_bruto = capital_operado + usdt_ganancia_equivalente
    saldo_boveda += saldo_boveda_bruto
    
    # Decisión de retiro
    ganancia_retenida = 0.0
    ganancia_retirada = 0.0
    
    if confirmar_accion(f"\nRetirar ganancia ({formatear_moneda(ganancia_bruta_dia)})?"):
        # Retiramos la ganancia (USD)
        ganancia_retirada = ganancia_bruta_dia
        # Y la restamos de la bóveda (en USDT)
        saldo_boveda -= usdt_ganancia_equivalente
        print(f"[OK] Retiro: {formatear_moneda(ganancia_bruta_dia)}")
    else:
        ganancia_retenida = ganancia_bruta_dia
        print(f"[OK] Reinversion: {formatear_moneda(ganancia_bruta_dia)}")
    
    # Aplicar limite (USDT equivalente del LIMITE_FINAL_USD)
    # Usamos la tasa del día como proxy para el cálculo del límite en USDT
    limite_final_usdt = LIMITE_FINAL_USD / tasa_compra_promedio 
    
    if dia_actual == ciclo['dias_totales']:
        if saldo_boveda > limite_final_usdt:
            exceso = saldo_boveda - limite_final_usdt
            # Se resta la ganancia retenida por el equivalente en USD del exceso (aproximación)
            ganancia_retenida -= (exceso * tasa_compra_promedio) 
            saldo_boveda = limite_final_usdt
            print(f"\n[AVISO] Limite aplicado. Exceso: {formatear_moneda(exceso * tasa_compra_promedio)}")
    
    roi_dia = (ganancia_bruta_dia / capital_operado_usd_costo * 100) if capital_operado_usd_costo > 0 else 0
    
    # --- Cálculo de Tasa de Costo Final para la Bóveda del Día Siguiente (CORRECCIÓN 4) ---
    
    # 1. Costo USD de los USDT que quedaron sin operar
    costo_usdt_no_operados_usd = capital_no_operado * tasa_costo_boveda 
    
    # 2. Costo USD de la Ganancia Retenida
    costo_ganancia_retenida_usd = ganancia_retenida # Ya está en USD
    
    # 3. Costo USD total de los USDT remanentes en la bóveda
    costo_total_boveda_usd = costo_usdt_no_operados_usd + costo_ganancia_retenida_usd
    
    if saldo_boveda > 0:
        # Tasa_Costo_Final = (Costo USD Total del saldo final) / (USDT Total del saldo final)
        tasa_costo_final = costo_total_boveda_usd / saldo_boveda
    else:
        tasa_costo_final = 1.0 
    
    # GUARDAR EN BD
    dia_data = {
        'dia_numero': dia_actual,
        'fecha': date.today(),
        'capital_disponible_inicio': capital_disponible_inicio, # USDT
        'capital_operado': capital_operado_usd_costo, # USD COSTO
        'capital_no_operado': capital_no_operado, # USDT
        'capital_fresco_inyectado': capital_fresco, # USD
        'saldo_boveda_final': saldo_boveda, # USDT
        'ganancia_bruta_dia': ganancia_bruta_dia, # USD
        'ganancia_retenida': ganancia_retenida, # USD
        'ganancia_retirada': ganancia_retirada, # USD
        'roi_dia': roi_dia,
        'tipo_operacion': tipo_operacion,
        'tasa_costo_final': tasa_costo_final # CAMPO NUEVO
    }
    
    dia_id = db.registrar_dia(ciclo_id, USUARIO_ID, dia_data)
    
    # Guardar cada venta
    for i, monto in enumerate(ventas_montos, 1):
        resultado = calcular_venta_individual(
            monto, tasa_venta_publicada, tasa_compra_promedio, COMISION_P2P_MAKER
        )
        
        venta_data = {
            'venta_numero': i,
            'monto_operado': monto,
            'usdt_operado': resultado['usdt_operado'],
            'tasa_venta_p2p': tasa_venta_publicada,
            'tasa_compra': tasa_compra_promedio,
            'comision_monto': resultado['comision_monto'],
            'comision_porcentaje': COMISION_P2P_MAKER,
            'ingreso_bruto': resultado['ingreso_bruto'],
            'ingreso_neto': resultado['ingreso_neto'],
            'ganancia_venta': resultado['ganancia_venta']
        }
        
        db.registrar_venta(dia_id, venta_data)
    
    # RESUMEN FINAL DEL DIA
    imprimir_titulo("RESUMEN DEL DIA")
    print(f"\n[OK] Dia {dia_actual} completado")
    print(f"   Capital operado:       {formatear_moneda(capital_operado_usd_costo)}") # Usar costo USD
    print(f"   Ventas completadas:  {len(ventas_montos)}")
    print(f"   Ganancia bruta:      {formatear_moneda(ganancia_bruta_dia)}")
    print(f"   Ganancia retenida:   {formatear_moneda(ganancia_retenida)}")
    print(f"   Ganancia retirada:   {formatear_moneda(ganancia_retirada)}")
    print(f"   Saldo boveda (USDT): {saldo_boveda:.4f} USDT") # Mostrar en USDT
    print(f"   ROI dia:             {formatear_porcentaje(roi_dia)}")
    print(f"   Tasa Costo Final:    {tasa_costo_final:.4f} USD/USDT") # Mostrar tasa final
    imprimir_separador()
    
    # Verificar si es el ultimo dia
    if dia_actual == ciclo['dias_totales']:
        # Se pasa el capital final en USD (costo) para el registro
        capital_final_usd = saldo_boveda * tasa_costo_final
        
        db.finalizar_ciclo(
            ciclo_id=ciclo_id,
            capital_final=capital_final_usd,
            ganancia_total=capital_final_usd - ciclo['capital_inicial'],
            roi_total=((capital_final_usd - ciclo['capital_inicial']) / ciclo['capital_inicial']) * 100
        )
        resumen_final_ciclo(db, ciclo_id)
    else:
        print(f"\n-> Listo para operar Dia {dia_actual + 1}")
    
    db.cerrar()

def menu_principal():
    """Menu principal del sistema"""
    
    while True:
        db = ArbitrajeDB()
        ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
        
        imprimir_titulo("CONTROL DE ARBITRAJE P2P v3.0 - MENU PRINCIPAL")
        print("\n1. Ejecutar Operacion del Dia")
        print("2. Ver Ciclo Actual")
        print("3. Historial de Ventas")
        print("4. Estadisticas")
        print("5. Crear Backup")
        print("6. [TEST] RESET COMPLETO - Borrar todo")
        print("7. Salir")
        imprimir_separador()
        
        opcion = input("\nOpcion (1-7): ").strip()
        
        if opcion == "1":
            ejecutar_dia()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "2":
            
            if ciclo:
                print(f"\n[CICLO ACTIVO]:")
                print(f"   ID: {ciclo['id']}")
                print(f"   Nombre: {ciclo['nombre_ciclo']}")
                print(f"   Dias: {ciclo['dias_completados']}/{ciclo['dias_totales']}")
                print(f"   Capital inicial: {formatear_moneda(ciclo['capital_inicial'])}")
                
                ultimo_dia = db.obtener_ultimo_dia(ciclo['id'])
                if ultimo_dia:
                    # Mostrar el valor USD real de la bóveda
                    saldo_usd_actual = ultimo_dia['saldo_boveda_final'] * ultimo_dia['tasa_costo_final']
                    print(f"   Saldo actual: {formatear_moneda(saldo_usd_actual)}")
            else:
                print("\n[AVISO] No hay ciclo activo")
            db.cerrar()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "3":
            
            if ciclo:
                cursor = db.conn.cursor()
                cursor.execute("""
                    SELECT v.*, d.dia_numero, d.fecha
                    FROM ventas v
                    JOIN dias d ON v.dia_id = d.id
                    WHERE d.ciclo_id = ?
                    ORDER BY d.dia_numero, v.venta_numero
                    LIMIT 20
                """, (ciclo['id'],))
                ventas = cursor.fetchall()
                
                if ventas:
                    print(f"\n[ULTIMAS 20 VENTAS]:")
                    print(f"{'Dia':<5} {'#':<3} {'Monto':<12} {'USDT':<10} {'Ganancia':<12}")
                    imprimir_separador("-", 60)
                    for v in ventas:
                        print(f"{v['dia_numero']:<5} #{v['venta_numero']:<2} "
                              f"{formatear_moneda(v['monto_operado']):<12} "
                              f"{v['usdt_operado']:>8.2f} "
                              f"{formatear_moneda(v['ganancia_venta']):<12}")
                else:
                    print("\n[AVISO] Sin ventas registradas")
            else:
                print("\n[AVISO] No hay ciclo activo")
            db.cerrar()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "4":
            
            if ciclo:
                stats = db.get_estadisticas_ciclo(ciclo['id'])
                print(f"\n[ESTADISTICAS DEL CICLO]:")
                print(f"   Total dias:      {stats['total_dias']}")
                print(f"   Total ventas:    {stats['total_ventas']}")
                print(f"   USDT operado:    {stats['total_usdt']:.2f} USDT")
                print(f"   Comisiones:      {formatear_moneda(stats['total_comisiones'])}")
                print(f"   Ganancia total:  {formatear_moneda(stats['ganancia_total'])}")
                print(f"   Promedio/dia:    {formatear_moneda(stats['ganancia_promedio'])}")
            else:
                print("\n[AVISO] No hay ciclo activo")
            db.cerrar()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "5":
            import shutil
            from datetime import datetime
            
            # Crear directorio si no existe
            backup_dir = 'data/backups'
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}/arbitraje_{timestamp}.db"
            
            if os.path.exists('data/arbitraje.db'):
                shutil.copy2('data/arbitraje.db', backup_file)
                tamano = os.path.getsize(backup_file)
                print(f"\n[OK] Backup creado:")
                print(f"   Archivo: {backup_file}")
                print(f"   Tamano: {tamano/1024:.2f} KB")
            else:
                print("\n[AVISO] No hay base de datos para respaldar")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "6":
            print("\n[PELIGRO] RESET COMPLETO - SOLO PARA PRUEBAS [PELIGRO]")
            print("\nEsto borrara:")
            print("  - Todos los ciclos")
            print("  - Todas las operaciones")
            print("  - Todo el historial")
            print("  - BASE DE DATOS COMPLETA\n")
            
            if confirmar_accion("ESTAS SEGURO?"):
                if confirmar_accion("REALMENTE seguro? (Ultima confirmacion)"):
                    import shutil
                    from datetime import datetime
                    
                    # Hacer backup antes de borrar
                    if os.path.exists('data/arbitraje.db'):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup = f"data/backups/BEFORE_RESET_{timestamp}.db"
                        os.makedirs('data/backups', exist_ok=True)
                        shutil.copy2('data/arbitraje.db', backup)
                        print(f"[OK] Backup guardado: {backup}")
                    
                    # Borrar base de datos
                    if os.path.exists('data/arbitraje.db'):
                        os.remove('data/arbitraje.db')
                    
                    print("\n[OK] RESET COMPLETO - Base de datos eliminada")
                    print("Al ejecutar la proxima operacion se creara una BD nueva\n")
                else:
                    print("\nReset cancelado")
            else:
                print("\nReset cancelado")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "7":
            print("\n[DESPEDIDA] Hasta luego!")
            break
        
        else:
            print("Opcion invalida (1-7)")
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n[AVISO] Operacion interrumpida")
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()