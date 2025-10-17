# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: arbitraje_core.py
# DESCRIPCION: Clase base con logica de arbitraje - CORREGIDA
# VERSION: 2.1 - Nomenclatura correcta: DIAS vs VENTAS
# ==========================================================

import math

class CicloArbitraje:
    """
    Clase que encapsula los parametros, tasas y la logica de calculo.
    
    CONCEPTOS CLAVE:
    - CICLO = Periodo completo de dias (ej: 30 dias)
    - DIA = Una jornada de operacion
    - VENTA = Operacion P2P individual dentro de un dia
    """
    
    def __init__(self, 
                 capital_inicial_usd: float, 
                 tasa_venta_p2p_publicada: float,
                 costo_compra_usdt: float,
                 comision_p2p_maker: float,
                 dias_ciclo: int,             
                 limite_final_usd: float,     
                 max_ventas_diarias: int):    
        """
        Inicializa el ciclo con todos los parametros de costo, tasas y limites.
        
        Args:
            capital_inicial_usd: Capital con el que inicia el dia
            tasa_venta_p2p_publicada: Tasa a la que publicas en P2P
            costo_compra_usdt: Costo de compra del USDT (tarjeta o 1.0 si es reinversion)
            comision_p2p_maker: Comision de Binance P2P
            dias_ciclo: Total de dias del ciclo completo
            limite_final_usd: Meta de capital al final del ciclo
            max_ventas_diarias: Maximo de ventas permitidas por dia
        """
        self.capital_inicial = capital_inicial_usd
        self.tasa_venta_p2p_publicada = tasa_venta_p2p_publicada
        self.COSTO_COMPRA_TARJETA = costo_compra_usdt
        self.COMISION_BINANCE_P2P = comision_p2p_maker
        
        self.DIAS_CICLO = dias_ciclo
        self.LIMITE_FINAL_USD = limite_final_usd
        self.MAX_VENTAS_DIARIAS = max_ventas_diarias
        
        self._calcular_tasas_derivadas()

    def _calcular_tasas_derivadas(self):
        """
        Calcula la tasa neta de venta y el factor de rentabilidad por venta.
        """
        self.tasa_venta_neta = self.tasa_venta_p2p_publicada * (1 - self.COMISION_BINANCE_P2P)
        
        self.tasa_rentabilidad_por_venta = (self.tasa_venta_neta / self.COSTO_COMPRA_TARJETA) - 1
        
        if self.tasa_rentabilidad_por_venta < 0:
            raise ValueError("La tasa de arbitraje es negativa o cero. No es rentable con estos costos.")

    def calcular_capital_final_proyectado(self, tasa_rentabilidad_promedio: float, dias: int) -> float:
        """Calcula el capital final proyectado (usado para ajustar el capital inicial)."""
        factor_crecimiento = (1 + tasa_rentabilidad_promedio) ** dias
        capital_final = self.capital_inicial * factor_crecimiento
        
        if capital_final > self.LIMITE_FINAL_USD and dias == self.DIAS_CICLO:
            return self.LIMITE_FINAL_USD
        
        return capital_final

    def calcular_ganancia_neta(self, capital_inicial_dia: float, ventas_completadas: int) -> float:
        """
        Calcula la ganancia neta en USD para un dia dado, basado en las ventas completadas.
        
        LOGICA DE INTERES COMPUESTO DENTRO DEL DIA:
        - Venta 1: Operas con capital inicial
        - Venta 2: Operas con capital inicial + ganancia venta 1
        - Venta 3: Operas con todo lo acumulado
        """
        factor_ganancia_dia = (1 + self.tasa_rentabilidad_por_venta) ** ventas_completadas
        capital_final_bruto = capital_inicial_dia * factor_ganancia_dia
        return capital_final_bruto - capital_inicial_dia

    def calcular_usdt_comprado(self, capital_inicial_dia: float, ventas_completadas: int) -> float:
        """
        Calcula el volumen total de USDT comprado/vendido en un dia.
        Suma todas las ventas con reinversion del dia.
        """
        usdt_total = 0
        capital_temporal = capital_inicial_dia
        
        for _ in range(ventas_completadas):
            usdt_comprado_venta = capital_temporal / self.COSTO_COMPRA_TARJETA
            usdt_total += usdt_comprado_venta
            
            ganancia_venta = capital_temporal * self.tasa_rentabilidad_por_venta
            capital_temporal += ganancia_venta
        
        return usdt_total

    def get_rentabilidad_porcentual_por_venta(self) -> float:
        """Retorna la rentabilidad por venta como porcentaje."""
        return self.tasa_rentabilidad_por_venta * 100
    
    def get_tasa_rentabilidad_por_venta(self) -> float:
        """Retorna la tasa de rentabilidad por venta como factor."""
        return self.tasa_rentabilidad_por_venta
    
    # ========== METODOS ADICIONALES ==========
    
    def get_tasa_minima_competitiva(self, margen_competitividad=0.02):
        """Calcula la tasa minima para ser competitivo en P2P"""
        return self.COSTO_COMPRA_TARJETA * (1 + margen_competitividad) / (1 - self.COMISION_BINANCE_P2P)
    
    def es_rentable(self, tasa_venta_propuesta: float) -> tuple:
        """Valida si una tasa propuesta es rentable y retorna (es_rentable, spread, roi)"""
        tasa_neta = tasa_venta_propuesta * (1 - self.COMISION_BINANCE_P2P)
        spread = (tasa_neta / self.COSTO_COMPRA_TARJETA) - 1
        roi_estimado = spread * 100
        return (spread > 0, spread, roi_estimado)
    
    def breakdown_operacion(self, capital_usd: float, ventas: int) -> dict:
        """
        Retorna un desglose detallado de la operacion del dia
        
        Args:
            capital_usd: Capital que se va a operar hoy
            ventas: Numero de ventas a completar hoy
        """
        usdt_comprado = self.calcular_usdt_comprado(capital_usd, ventas)
        ganancia_neta = self.calcular_ganancia_neta(capital_usd, ventas_completadas=ventas)
        
        ingreso_bruto_venta = usdt_comprado * self.tasa_venta_p2p_publicada
        comisiones_totales = usdt_comprado * self.tasa_venta_p2p_publicada * self.COMISION_BINANCE_P2P
        
        return {
            'capital_inicial': capital_usd,
            'ventas_completadas': ventas,
            'usdt_total_operado': usdt_comprado,
            'costo_total_compra': capital_usd,
            'ingreso_bruto_venta': ingreso_bruto_venta,
            'comisiones_p2p': comisiones_totales,
            'ingreso_neto_venta': ingreso_bruto_venta - comisiones_totales,
            'ganancia_neta': ganancia_neta,
            'capital_final': capital_usd + ganancia_neta,
            'roi_dia': (ganancia_neta / capital_usd) * 100,
            'rentabilidad_por_venta': self.get_rentabilidad_porcentual_por_venta()
        }
    
    def breakdown_venta_por_venta(self, capital_usd: float, ventas: int) -> list:
        """
        Retorna el desglose de CADA venta individual del dia
        Util para ver el interes compuesto en accion
        """
        ventas_detalle = []
        capital_temporal = capital_usd
        
        for num_venta in range(1, ventas + 1):
            usdt_venta = capital_temporal / self.COSTO_COMPRA_TARJETA
            ingreso_bruto = usdt_venta * self.tasa_venta_p2p_publicada
            comision = ingreso_bruto * self.COMISION_BINANCE_P2P
            ingreso_neto = ingreso_bruto - comision
            ganancia = ingreso_neto - capital_temporal
            
            ventas_detalle.append({
                'venta_num': num_venta,
                'capital_entrada': capital_temporal,
                'usdt_operado': usdt_venta,
                'ingreso_bruto': ingreso_bruto,
                'comision': comision,
                'ingreso_neto': ingreso_neto,
                'ganancia_venta': ganancia,
                'capital_salida': ingreso_neto
            })
            
            capital_temporal = ingreso_neto
        
        return ventas_detalle
    
    def calcular_comision_total(self, capital_usd: float, ventas: int) -> float:
        """Calcula el total de comisiones pagadas en la operacion del dia"""
        usdt_total = self.calcular_usdt_comprado(capital_usd, ventas)
        return usdt_total * self.tasa_venta_p2p_publicada * self.COMISION_BINANCE_P2P
