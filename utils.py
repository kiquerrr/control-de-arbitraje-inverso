# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: utils.py
# DESCRIPCION: Utilidades y funciones auxiliares
# ==========================================================

import os
import shutil
from datetime import datetime

def crear_backup(archivo: str) -> bool:
    """Crea un backup del archivo con timestamp"""
    if not os.path.exists(archivo):
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta_backup = 'data/backups'
    os.makedirs(carpeta_backup, exist_ok=True)
    
    nombre_archivo = os.path.basename(archivo)
    backup_path = f"{carpeta_backup}/{nombre_archivo}.{timestamp}.backup"
    
    try:
        shutil.copy2(archivo, backup_path)
        print(f"? Backup creado: {backup_path}")
        return True
    except Exception as e:
        print(f"?? Error al crear backup: {e}")
        return False

def validar_numero_positivo(prompt: str, default=None, maximo=None) -> float:
    """Valida entrada numerica positiva con valor por defecto opcional"""
    while True:
        try:
            entrada = input(prompt)
            
            if not entrada and default is not None:
                return default
            
            valor = float(entrada)
            
            if valor <= 0:
                print("? El valor debe ser positivo.")
                continue
            
            if maximo and valor > maximo:
                print(f"? El valor excede el máximo permitido ({maximo}).")
                continue
            
            return valor
        except ValueError:
            print("? Entrada no válida. Ingrese un número.")

def validar_entero_rango(prompt: str, minimo: int, maximo: int) -> int:
    """Valida entrada de entero dentro de un rango"""
    while True:
        try:
            valor = int(input(prompt))
            if minimo <= valor <= maximo:
                return valor
            else:
                print(f"? El valor debe estar entre {minimo} y {maximo}.")
        except ValueError:
            print("? Entrada no válida. Ingrese un número entero.")

def confirmar_accion(mensaje: str) -> bool:
    """Solicita confirmación S/N"""
    while True:
        respuesta = input(f"{mensaje} (S/N): ").upper().strip()
        if respuesta in ['S', 'SI', 'Y', 'YES']:
            return True
        elif respuesta in ['N', 'NO']:
            return False
        else:
            print("? Respuesta no válida. Use S o N.")

def formatear_moneda(valor: float) -> str:
    """Formatea un valor como moneda USD"""
    return f"${valor:,.2f}"

def formatear_porcentaje(valor: float, decimales: int = 2) -> str:
    """Formatea un valor como porcentaje"""
    return f"{valor:.{decimales}f}%"

def imprimir_separador(caracter="=", longitud=80):
    """Imprime una línea separadora"""
    print(caracter * longitud)

def imprimir_titulo(titulo: str, caracter="="):
    """Imprime un título centrado con separadores"""
    longitud = 80
    imprimir_separador(caracter, longitud)
    print(titulo.center(longitud))
    imprimir_separador(caracter, longitud)

def limpiar_pantalla():
    """Limpia la pantalla de la consola"""
    os.system('clear' if os.name == 'posix' else 'cls')