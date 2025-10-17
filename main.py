# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: main.py
# VERSION: 3.0 - Con BD SQLite y ventas individuales
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
    capital_restante = capital_disponible
    
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
        while True:
            monto = validar_numero_positivo(
                f"  Venta #{i} - Monto operado: $",
                maximo=capital_restante
            )
            
            if monto > capital_restante:
                print(f"  ⚠️ Error: Solo quedan {formatear_moneda(capital_restante)} disponibles")
                continue
            
            ventas.append(monto)
            capital_restante -= monto
            print(f"  ✅ Registrada. Restante: {formatear_moneda(capital_restante)}\n")
            break
    
    total_operado = sum(ventas)
    
    if capital_restante > 0.01:
        usar_resto = confirmar_accion(
            f"\nQuedan {formatear_moneda(capital_restante)} sin operar. Agregar como venta adicional?"
        )
        if usar_resto:
            ventas.append(capital_restante)
            capital_restante = 0
    
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
    
    print(f"\n📊 RESUMEN DEL DIA:")
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
        SELECT saldo_boveda_final 
        FROM dias 
        WHERE ciclo_id = ? 
        ORDER BY dia_numero DESC 
        LIMIT 1
    """, (ciclo_id,))
    ultimo_saldo = cursor.fetchone()
    
    capital_inicial = ciclo['capital_inicial']
    capital_final = ciclo['capital_final'] if ciclo['capital_final'] else (ultimo_saldo[0] if ultimo_saldo else capital_inicial)
    ganancia_total = capital_final - capital_inicial
    roi_total = (ganancia_total / capital_inicial * 100) if capital_inicial > 0 else 0
    
    imprimir_titulo("RESUMEN FINAL DEL CICLO")
    
    print(f"\n📅 CICLO: {ciclo['nombre_ciclo']}")
    print(f"   Duracion: {ciclo['dias_totales']} dias ({stats['total_dias']} completados)")
    print(f"   Fecha inicio: {ciclo['fecha_inicio']}")
    print(f"   Fecha fin: {ciclo['fecha_fin']}")
    
    print(f"\n💰 RESULTADOS FINANCIEROS:")
    print(f"   Capital inicial:  {formatear_moneda(capital_inicial)}")
    print(f"   Capital final:    {formatear_moneda(capital_final)}")
    print(f"   Ganancia total:   {formatear_moneda(ganancia_total)}")
    print(f"   ROI total:        {formatear_porcentaje(roi_total)}")
    
    if ciclo['dias_totales'] > 0:
        roi_diario = ((capital_final / capital_inicial) ** (1/ciclo['dias_totales']) - 1) * 100
        print(f"   ROI diario (compuesto): {formatear_porcentaje(roi_diario, 3)}")
    
    print(f"\n📊 OPERACIONES:")
    print(f"   Total ventas:     {stats_ventas['total_ventas']}")
    print(f"   USDT operado:     {stats_ventas['total_usdt']:.2f} USDT")
    print(f"   Comisiones:       {formatear_moneda(stats_ventas['total_comisiones'])}")
    
    # Plan de ahorro BTC
    monto_btc = ganancia_total * PORCENTAJE_AHORRO_BTC
    monto_proximo = capital_final - monto_btc
    
    print(f"\n💎 PLAN DE AHORRO:")
    print(f"   Para BTC ({PORCENTAJE_AHORRO_BTC*100:.0f}%):  {formatear_moneda(monto_btc)}")
    print(f"   Proximo ciclo:   {formatear_moneda(monto_proximo)}")
    
    imprimir_separador()


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
        
        capital_inicial = validar_numero_positivo(
            "-> Capital inicial del ciclo: $"
        )
        
        nombre_ciclo = input("-> Nombre del ciclo (Enter para auto): ").strip()
        
        ciclo_id = db.iniciar_ciclo(
            usuario_id=USUARIO_ID,
            dias_totales=dias_totales,
            capital_inicial=capital_inicial,
            nombre_ciclo=nombre_ciclo if nombre_ciclo else None
        )
        
        ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
        saldo_boveda = capital_inicial
        dia_actual = 1
        
        print(f"\n✅ Ciclo iniciado: {ciclo['nombre_ciclo']}")
        print(f"   ID: {ciclo_id}")
        print(f"   Capital inicial: {formatear_moneda(capital_inicial)}")
        
    else:
        # CONTINUAR CICLO EXISTENTE
        ciclo_id = ciclo['id']
        ultimo_dia = db.obtener_ultimo_dia(ciclo_id)
        
        if ultimo_dia:
            dia_actual = ultimo_dia['dia_numero'] + 1
            saldo_boveda = ultimo_dia['saldo_boveda_final']
        else:
            dia_actual = 1
            saldo_boveda = ciclo['capital_inicial']
        
        # Verificar si el ciclo ya termino
        if dia_actual > ciclo['dias_totales']:
            print(f"\n✅ CICLO FINALIZADO")
            resumen_final_ciclo(db, ciclo_id)
            
            if confirmar_accion("\nIniciar nuevo ciclo?"):
                db.finalizar_ciclo(
                    ciclo_id=ciclo_id,
                    capital_final=saldo_boveda,
                    ganancia_total=saldo_boveda - ciclo['capital_inicial'],
                    roi_total=((saldo_boveda - ciclo['capital_inicial']) / ciclo['capital_inicial']) * 100
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
    print(f"SALDO EN BOVEDA: {formatear_moneda(saldo_boveda)}")
    print(f"{'='*60}")
    
    # PASO 1: DECISION DE CAPITAL A OPERAR
    capital_disponible_inicio = saldo_boveda
    capital_operado = 0.0
    capital_no_operado = 0.0
    capital_fresco = 0.0
    tipo_operacion = ""
    tasa_compra_promedio = COSTO_COMPRA_BASE
    
    if saldo_boveda > 0 and dia_actual > 1:
        # HAY SALDO
        print(f"\n💰 OPCIONES DE CAPITAL:")
        print("   1. Operar TODO el saldo")
        print("   2. Operar PARTE del saldo")
        print("   3. Solo inyectar capital FRESCO")
        print("   4. Operar PARTE + capital FRESCO")
        
        opcion = input("\nOpcion (1-4): ").strip()
        
        if opcion == "1":
            capital_operado = saldo_boveda
            capital_no_operado = 0.0
            tasa_compra_promedio = 1.0
            tipo_operacion = "REINVERSION_TOTAL"
            
        elif opcion == "2":
            capital_operado = validar_numero_positivo(
                f"Monto a operar (Max {formatear_moneda(saldo_boveda)}): $",
                maximo=saldo_boveda
            )
            capital_no_operado = saldo_boveda - capital_operado
            tasa_compra_promedio = 1.0
            tipo_operacion = "REINVERSION_PARCIAL"
            
        elif opcion == "3":
            capital_no_operado = saldo_boveda
            capital_fresco = validar_numero_positivo("Monto FRESCO a comprar: $")
            capital_operado = capital_fresco
            tasa_compra_promedio = validar_numero_positivo(
                f"Costo USDT/Tarjeta (Sugerido {COSTO_COMPRA_BASE:.4f}): $",
                default=COSTO_COMPRA_BASE
            )
            tipo_operacion = "CAPITAL_FRESCO_PURO"
            
        elif opcion == "4":
            cap_boveda = validar_numero_positivo(
                f"Monto de boveda (Max {formatear_moneda(saldo_boveda)}): $",
                maximo=saldo_boveda
            )
            capital_fresco = validar_numero_positivo("Monto FRESCO a comprar: $")
            costo_fresco = validar_numero_positivo(
                f"Costo USDT del fresco (Sugerido {COSTO_COMPRA_BASE:.4f}): $",
                default=COSTO_COMPRA_BASE
            )
            
            capital_operado = cap_boveda + capital_fresco
            capital_no_operado = saldo_boveda - cap_boveda
            tasa_compra_promedio = (cap_boveda * 1.0 + capital_fresco * costo_fresco) / capital_operado
            tipo_operacion = "REINVERSION_MIXTA"
            
            print(f"\n  Boveda: {formatear_moneda(cap_boveda)}")
            print(f"  Fresco: {formatear_moneda(capital_fresco)}")
            print(f"  Total:  {formatear_moneda(capital_operado)}")
            print(f"  Costo ponderado: {tasa_compra_promedio:.4f} USD/USDT")
        else:
            print("Opcion invalida")
            db.cerrar()
            return
    else:
        # DIA 1 - Verificar si hay saldo de ciclo anterior
        if saldo_boveda > 0:
            print(f"\n💰 Hay saldo en bóveda: {formatear_moneda(saldo_boveda)}")
            usar_saldo = confirmar_accion("Usar este saldo para operar?")
            
            if usar_saldo:
                capital_operado = saldo_boveda
                capital_no_operado = 0.0
                tasa_compra_promedio = 1.0
                tipo_operacion = "SALDO_ANTERIOR"
            else:
                # Quiere inyectar capital fresco
                capital_no_operado = saldo_boveda
                capital_fresco = validar_numero_positivo("Monto FRESCO a comprar: $")
                capital_operado = capital_fresco
                tasa_compra_promedio = validar_numero_positivo(
                    f"Costo USDT/Tarjeta (Sugerido {COSTO_COMPRA_BASE:.4f}): $",
                    default=COSTO_COMPRA_BASE
                )
                tipo_operacion = "CAPITAL_FRESCO_DIA1"
        else:
            # No hay saldo, obligado a inyectar
            print(f"\n💳 CAPITAL INICIAL REQUERIDO")
            capital_fresco = validar_numero_positivo("Monto a COMPRAR (tarjeta): $")
            capital_operado = capital_fresco
            tasa_compra_promedio = validar_numero_positivo(
                f"Costo USDT/Tarjeta (Sugerido {COSTO_COMPRA_BASE:.4f}): $",
                default=COSTO_COMPRA_BASE
            )
            tipo_operacion = "CAPITAL_INICIAL"
    
    # Retirar capital de boveda
    saldo_boveda -= capital_operado
    
    # PASO 2: TASA DE VENTA P2P
    print(f"\n📊 CONFIGURACION DE VENTA P2P")
    print("\n⚠️  IMPORTANTE: Consulta la tasa promedio en:")
    print("    Binance P2P > Vender USDT > Ver anuncios de COMPRA")
    print("    (Esa es la tasa a la que otros COMPRAN tu USDT)\n")
    
    tasa_p2p_mercado = validar_numero_positivo(
        "Tasa promedio del mercado P2P BINANCE de hoy: $"
    )
    
    # Calcular punto de equilibrio
    punto_equilibrio = tasa_compra_promedio / (1 - COMISION_P2P_MAKER)
    
    print(f"\n💡 ANALISIS DE RENTABILIDAD:")
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
            print(f"\n❌ ERROR: Tasa por DEBAJO del punto de equilibrio!")
            print(f"   Tu tasa:    {tasa_venta_publicada:.4f}")
            print(f"   Minimo:     {punto_equilibrio:.4f}")
            print(f"   PERDERIAS DINERO con esta tasa.\n")
            
            if not confirmar_accion("Reintentar con otra tasa?"):
                saldo_boveda += capital_operado
                db.cerrar()
                return
            continue
        
        # Calcular margen
        tasa_neta = tasa_venta_publicada * (1 - COMISION_P2P_MAKER)
        margen = ((tasa_neta / tasa_compra_promedio) - 1) * 100
        
        if margen <= 0:
            print(f"\n❌ Tasa NO rentable (Margen: {margen:.2f}%)")
            continue
        
        if margen < 0.5:
            print(f"\n⚠️  ADVERTENCIA: Margen muy bajo ({formatear_porcentaje(margen)})")
            if not confirmar_accion("Continuar con este margen?"):
                continue
        
        print(f"\n✅ Tasa rentable. Margen neto: {formatear_porcentaje(margen)}")
        break
    
    # PASO 3: REGISTRAR VENTAS DEL DIA
    ventas_montos = solicitar_ventas_del_dia(capital_operado, MAX_VENTAS_DIARIAS)
    
    # PREVIEW
    preview_totales = preview_ventas(
        ventas_montos, 
        tasa_venta_publicada, 
        tasa_compra_promedio, 
        COMISION_P2P_MAKER
    )
    
    if not confirmar_accion("\nConfirmar operacion del dia?"):
        print("\n❌ Operacion cancelada")
        saldo_boveda += capital_operado
        db.cerrar()
        return
    
    # REGISTRAR EN BD
    ganancia_bruta_dia = preview_totales['total_ganancia']
    capital_final_dia = capital_operado + ganancia_bruta_dia
    
    # Devolver a boveda
    saldo_boveda += capital_final_dia
    
    # Decisión de retiro
    ganancia_retenida = 0.0
    ganancia_retirada = 0.0
    
    if confirmar_accion(f"\nRetirar ganancia ({formatear_moneda(ganancia_bruta_dia)})?"):
        saldo_boveda -= ganancia_bruta_dia
        ganancia_retirada = ganancia_bruta_dia
        print(f"✅ Retiro: {formatear_moneda(ganancia_bruta_dia)}")
    else:
        ganancia_retenida = ganancia_bruta_dia
        print(f"✅ Reinversion: {formatear_moneda(ganancia_bruta_dia)}")
    
    # Aplicar limite
    if dia_actual == ciclo['dias_totales']:
        if saldo_boveda > LIMITE_FINAL_USD:
            exceso = saldo_boveda - LIMITE_FINAL_USD
            ganancia_retenida -= exceso
            saldo_boveda = LIMITE_FINAL_USD
            print(f"\n⚠️ Limite aplicado. Exceso: {formatear_moneda(exceso)}")
    
    roi_dia = (ganancia_bruta_dia / capital_operado * 100) if capital_operado > 0 else 0
    
    # GUARDAR EN BD
    dia_data = {
        'dia_numero': dia_actual,
        'fecha': date.today(),
        'capital_disponible_inicio': capital_disponible_inicio,
        'capital_operado': capital_operado,
        'capital_no_operado': capital_no_operado,
        'capital_fresco_inyectado': capital_fresco,
        'saldo_boveda_final': saldo_boveda,
        'ganancia_bruta_dia': ganancia_bruta_dia,
        'ganancia_retenida': ganancia_retenida,
        'ganancia_retirada': ganancia_retirada,
        'roi_dia': roi_dia,
        'tipo_operacion': tipo_operacion
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
    print(f"\n✅ Dia {dia_actual} completado")
    print(f"   Capital operado:     {formatear_moneda(capital_operado)}")
    print(f"   Ventas completadas:  {len(ventas_montos)}")
    print(f"   Ganancia bruta:      {formatear_moneda(ganancia_bruta_dia)}")
    print(f"   Ganancia retenida:   {formatear_moneda(ganancia_retenida)}")
    print(f"   Ganancia retirada:   {formatear_moneda(ganancia_retirada)}")
    print(f"   Saldo boveda:        {formatear_moneda(saldo_boveda)}")
    print(f"   ROI dia:             {formatear_porcentaje(roi_dia)}")
    imprimir_separador()
    
    # Verificar si es el ultimo dia
    if dia_actual == ciclo['dias_totales']:
        db.finalizar_ciclo(
            ciclo_id=ciclo_id,
            capital_final=saldo_boveda,
            ganancia_total=saldo_boveda - ciclo['capital_inicial'],
            roi_total=((saldo_boveda - ciclo['capital_inicial']) / ciclo['capital_inicial']) * 100
        )
        resumen_final_ciclo(db, ciclo_id)
    else:
        print(f"\n➡️  Listo para operar Dia {dia_actual + 1}")
    
    db.cerrar()

def menu_principal():
    """Menu principal del sistema"""
    
    while True:
        imprimir_titulo("CONTROL DE ARBITRAJE P2P v3.0 - MENU PRINCIPAL")
        print("\n1. Ejecutar Operacion del Dia")
        print("2. Ver Ciclo Actual")
        print("3. Historial de Ventas")
        print("4. Estadisticas")
        print("5. Crear Backup")
        print("6. Salir")
        imprimir_separador()
        
        opcion = input("\nOpcion (1-6): ").strip()
        
        if opcion == "1":
            ejecutar_dia()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "2":
            db = ArbitrajeDB()
            ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
            if ciclo:
                print(f"\n📊 CICLO ACTIVO:")
                print(f"   ID: {ciclo['id']}")
                print(f"   Nombre: {ciclo['nombre_ciclo']}")
                print(f"   Dias: {ciclo['dias_completados']}/{ciclo['dias_totales']}")
                print(f"   Capital inicial: {formatear_moneda(ciclo['capital_inicial'])}")
                
                ultimo_dia = db.obtener_ultimo_dia(ciclo['id'])
                if ultimo_dia:
                    print(f"   Saldo actual: {formatear_moneda(ultimo_dia['saldo_boveda_final'])}")
            else:
                print("\n⚠️ No hay ciclo activo")
            db.cerrar()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "3":
            db = ArbitrajeDB()
            ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
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
                    print(f"\n📋 ULTIMAS 20 VENTAS:")
                    print(f"{'Dia':<5} {'#':<3} {'Monto':<12} {'USDT':<10} {'Ganancia':<12}")
                    imprimir_separador("-", 60)
                    for v in ventas:
                        print(f"{v['dia_numero']:<5} #{v['venta_numero']:<2} "
                              f"{formatear_moneda(v['monto_operado']):<12} "
                              f"{v['usdt_operado']:>8.2f} "
                              f"{formatear_moneda(v['ganancia_venta']):<12}")
                else:
                    print("\n⚠️ Sin ventas registradas")
            else:
                print("\n⚠️ No hay ciclo activo")
            db.cerrar()
            input("\nPresione Enter para continuar...")
        
        elif opcion == "4":
            db = ArbitrajeDB()
            ciclo = db.obtener_ciclo_activo(usuario_id=USUARIO_ID)
            if ciclo:
                stats = db.get_estadisticas_ciclo(ciclo['id'])
                print(f"\n📊 ESTADISTICAS DEL CICLO:")
                print(f"   Total dias:      {stats['total_dias']}")
                print(f"   Total ventas:    {stats['total_ventas']}")
                print(f"   USDT operado:    {stats['total_usdt']:.2f} USDT")
                print(f"   Comisiones:      {formatear_moneda(stats['total_comisiones'])}")
                print(f"   Ganancia total:  {formatear_moneda(stats['ganancia_total'])}")
                print(f"   Promedio/dia:    {formatear_moneda(stats['ganancia_promedio'])}")
            else:
                print("\n⚠️ No hay ciclo activo")
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
                print(f"\n✅ Backup creado:")
                print(f"   Archivo: {backup_file}")
                print(f"   Tamaño: {tamano/1024:.2f} KB")
            else:
                print("\n⚠️ No hay base de datos para respaldar")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "6":
            print("\n👋 Hasta luego!")
            break
        
        else:
            print("❌ Opcion invalida")
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operacion interrumpida")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
