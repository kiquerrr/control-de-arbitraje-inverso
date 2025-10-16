# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: arbitraje_core.py
# DESCRIPCION: Clase base con logica de arbitraje mejorada.
# VERSION: 2.0
# ==========================================================

import math

class CicloArbitraje:
    """
    Clase que encapsula los parametros, tasas y la logica de calculo.
    VERSION MEJORADA con metodos adicionales de analisis.
    """
    
    def __init__(self, 
                 capital_inicial_usd: float, 
                 tasa_venta_p2p_publicada: float,
                 costo_compra_usdt: float,
                 comision_p2p_maker: float,
                 dias_ciclo: int,             
                 limite_final_usd: float,     
                 max_ciclos_diarios: int):    
        """
        Inicializa el ciclo con todos los parametros de costo, tasas y limites.
        """
        self.capital_inicial = capital_inicial_usd
        self.tasa_venta_p2p_publicada = tasa_venta_p2p_publicada
        self.COSTO_COMPRA_TARJETA = costo_compra_usdt
        self.COMISION_BINANCE_P2P = comision_p2p_maker
        
        self.DIAS_CICLO = dias_ciclo
        self.LIMITE_FINAL_USD = limite_final_usd
        self.MAX_CICLOS_DIARIOS = max_ciclos_diarios
        
        self._calcular_tasas_derivadas()

    def _calcular_tasas_derivadas(self):
        """
        Calcula la tasa neta de venta y el factor de rentabilidad por ciclo.
        """
        self.tasa_venta_neta = self.tasa_venta_p2p_publicada * (1 - self.COMISION_BINANCE_P2P)
        
        self.tasa_rentabilidad_por_ciclo = (self.tasa_venta_neta / self.COSTO_COMPRA_TARJETA) - 1
        
        if self.tasa_rentabilidad_por_ciclo < 0:
            raise ValueError("La tasa de arbitraje es negativa o cero. No es rentable con estos costos.")

    def calcular_capital_final_proyectado(self, tasa_rentabilidad_promedio: float, dias: int) -> float:
        """Calcula el capital final proyectado (usado para ajustar el capital inicial)."""
        factor_crecimiento = (1 + tasa_rentabilidad_promedio) ** dias
        capital_final = self.capital_inicial * factor_crecimiento
        
        if capital_final > self.LIMITE_FINAL_USD and dias == self.DIAS_CICLO:
            return self.LIMITE_FINAL_USD
        
        return capital_final

    def calcular_ganancia_neta(self, capital_inicial_dia: float, ciclos_completados: int) -> float:
        """Calcula la ganancia neta en USD para un dia dado, basado en los ciclos completados."""
        factor_ganancia_dia = (1 + self.tasa_rentabilidad_por_ciclo) ** ciclos_completados
        capital_final_bruto = capital_inicial_dia * factor_ganancia_dia
        return capital_final_bruto - capital_inicial_dia

    def calcular_usdt_comprado(self, capital_inicial_dia: float, ciclos_completados: int) -> float:
        """Calcula el volumen total de USDT comprado en un dia (sumando todas las reinversiones)."""
        usdt_total = 0
        capital_temporal = capital_inicial_dia
        
        for _ in range(ciclos_completados):
            usdt_comprado_ciclo = capital_temporal / self.COSTO_COMPRA_TARJETA
            usdt_total += usdt_comprado_ciclo
            
            ganancia_ciclo = capital_temporal * self.tasa_rentabilidad_por_ciclo
            capital_temporal += ganancia_ciclo
        
        return usdt_total

    def get_rentabilidad_porcentual_por_ciclo(self) -> float:
        """Retorna la rentabilidad por ciclo como porcentaje."""
        return self.tasa_rentabilidad_por_ciclo * 100
    
    def get_tasa_rentabilidad_por_ciclo(self) -> float:
        """Retorna la tasa de rentabilidad por ciclo como factor."""
        return self.tasa_rentabilidad_por_ciclo
    
    # ========== NUEVOS METODOS ==========
    
    def get_tasa_minima_competitiva(self, margen_competitividad=0.02):
        """Calcula la tasa minima para ser competitivo en P2P"""
        return self.COSTO_COMPRA_TARJETA * (1 + margen_competitividad) / (1 - self.COMISION_BINANCE_P2P)
    
    def es_rentable(self, tasa_venta_propuesta: float) -> tuple:
        """Valida si una tasa propuesta es rentable y retorna (es_rentable, spread, roi)"""
        tasa_neta = tasa_venta_propuesta * (1 - self.COMISION_BINANCE_P2P)
        spread = (tasa_neta / self.COSTO_COMPRA_TARJETA) - 1
        roi_estimado = spread * 100
        return (spread > 0, spread, roi_estimado)
    
    def breakdown_operacion(self, capital_usd: float, ciclos: int) -> dict:
        """Retorna un desglose detallado de la operacion"""
        usdt_comprado = self.calcular_usdt_comprado(capital_usd, ciclos)
        ganancia_neta = self.calcular_ganancia_neta(capital_usd, ciclos)
        
        ingreso_bruto_venta = usdt_comprado * self.tasa_venta_p2p_publicada
        comisiones_totales = usdt_comprado * self.tasa_venta_p2p_publicada * self.COMISION_BINANCE_P2P
        
        return {
            'capital_inicial': capital_usd,
            'ciclos_completados': ciclos,
            'usdt_total_comprado': usdt_comprado,
            'costo_total_compra': capital_usd,
            'ingreso_bruto_venta': ingreso_bruto_venta,
            'comisiones_p2p': comisiones_totales,
            'ingreso_neto_venta': ingreso_bruto_venta - comisiones_totales,
            'ganancia_neta': ganancia_neta,
            'capital_final': capital_usd + ganancia_neta,
            'roi_dia': (ganancia_neta / capital_usd) * 100,
            'rentabilidad_por_ciclo': self.get_rentabilidad_porcentual_por_ciclo()
        }
    
    def calcular_comision_total(self, capital_usd: float, ciclos: int) -> float:
        """Calcula el total de comisiones pagadas en la operacion"""
        usdt_total = self.calcular_usdt_comprado(capital_usd, ciclos)
        return usdt_total * self.tasa_venta_p2p_publicada * self.COMISION_BINANCE_P2P
