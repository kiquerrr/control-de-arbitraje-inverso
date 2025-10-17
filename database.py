# -*- coding: utf-8 -*-
# ==========================================================
# ARCHIVO: database.py
# DESCRIPCION: Gestion de base de datos SQLite - Version Profesional
# VERSION: 3.0 - Multi-usuario, Auditoria, Logs
# ==========================================================

import sqlite3
from datetime import datetime
import os
import hashlib

class ArbitrajeDB:
    def __init__(self, db_path='data/arbitraje.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.crear_tablas()
    
    def crear_tablas(self):
        """Crea todas las tablas del sistema"""
        cursor = self.conn.cursor()
        
        # TABLAS DE USUARIOS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE,
                rol TEXT DEFAULT 'OPERADOR',
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_sesion TIMESTAMP,
                notas TEXT
            )
        """)
        
        # TABLAS DE METODOS DE PAGO
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metodos_pago (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                tipo TEXT,
                nombre_tarjeta TEXT,
                ultimos_4_digitos TEXT,
                banco TEXT,
                costo_fijo_usdt REAL,
                comision_porcentaje REAL DEFAULT 0,
                limite_diario REAL,
                limite_mensual REAL,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # TABLAS OPERATIVAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ciclos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                nombre_ciclo TEXT,
                fecha_inicio DATE,
                fecha_fin DATE,
                dias_totales INTEGER,
                dias_completados INTEGER DEFAULT 0,
                capital_inicial REAL,
                capital_final REAL,
                ganancia_total REAL,
                roi_total REAL,
                estado TEXT DEFAULT 'ACTIVO',
                notas TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER,
                usuario_id INTEGER,
                dia_numero INTEGER,
                fecha DATE,
                capital_disponible_inicio REAL,
                capital_operado REAL,
                capital_no_operado REAL,
                capital_fresco_inyectado REAL,
                metodo_pago_id INTEGER,
                saldo_boveda_final REAL,
                ganancia_bruta_dia REAL,
                ganancia_retenida REAL,
                ganancia_retirada REAL,
                roi_dia REAL,
                tipo_operacion TEXT,
                notas TEXT,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (metodo_pago_id) REFERENCES metodos_pago(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia_id INTEGER,
                venta_numero INTEGER,
                monto_operado REAL,
                usdt_operado REAL,
                tasa_venta_p2p REAL,
                tasa_compra REAL,
                comision_monto REAL,
                comision_porcentaje REAL,
                ingreso_bruto REAL,
                ingreso_neto REAL,
                ganancia_venta REAL,
                orden_p2p_id TEXT,
                contraparte_username TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dia_id) REFERENCES dias(id)
            )
        """)
        
        # TABLAS CONTABLES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_contables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER,
                dia_id INTEGER,
                venta_id INTEGER,
                usuario_id INTEGER,
                tipo_movimiento TEXT,
                concepto TEXT,
                debe REAL DEFAULT 0,
                haber REAL DEFAULT 0,
                saldo_acumulado REAL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referencia TEXT,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (dia_id) REFERENCES dias(id),
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                tabla_afectada TEXT,
                registro_id INTEGER,
                accion TEXT,
                datos_anteriores TEXT,
                datos_nuevos TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conciliaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER,
                fecha_conciliacion DATE,
                saldo_sistema REAL,
                saldo_binance REAL,
                saldo_banco REAL,
                diferencia REAL,
                estado TEXT DEFAULT 'PENDIENTE',
                observaciones TEXT,
                conciliado_por INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (conciliado_por) REFERENCES usuarios(id)
            )
        """)
        
        # TABLAS DE LOGS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nivel TEXT,
                modulo TEXT,
                funcion TEXT,
                mensaje TEXT,
                datos_extra TEXT,
                usuario_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_error TEXT,
                mensaje_error TEXT,
                stack_trace TEXT,
                contexto TEXT,
                usuario_id INTEGER,
                resuelto INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                archivo_path TEXT,
                tamano_bytes INTEGER,
                md5_hash TEXT,
                usuario_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # TABLAS DE LICENCIAS (Para futuro sistema de venta)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_licencia TEXT UNIQUE NOT NULL,
                tipo_licencia TEXT,
                usuario_id INTEGER,
                fecha_activacion DATE,
                fecha_expiracion DATE,
                dispositivos_max INTEGER DEFAULT 1,
                estado TEXT DEFAULT 'ACTIVA',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                licencia_id INTEGER,
                hardware_id TEXT,
                ip_address TEXT,
                fecha_activacion TIMESTAMP,
                ultima_conexion TIMESTAMP,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY (licencia_id) REFERENCES licencias(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validaciones_licencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                licencia_id INTEGER,
                fecha_validacion TIMESTAMP,
                resultado TEXT,
                ip_address TEXT,
                FOREIGN KEY (licencia_id) REFERENCES licencias(id)
            )
        """)
        
        # CONFIGURACION
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                tipo_dato TEXT,
                descripcion TEXT,
                actualizado_por INTEGER,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (actualizado_por) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parametros_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                valor TEXT,
                tipo TEXT,
                categoria TEXT,
                descripcion TEXT,
                modificable INTEGER DEFAULT 1,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # INDICES
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ciclos_usuario ON ciclos(usuario_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ciclos_estado ON ciclos(estado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dias_ciclo ON dias(ciclo_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dias_fecha ON dias(fecha)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_dia ON ventas(dia_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_nivel ON logs_sistema(nivel)')
        
        self.conn.commit()
        self.crear_usuario_default()
        self.insertar_parametros_default()
    
    def crear_usuario_default(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, rol, activo)
                VALUES ('Operador Principal', 'admin@arbitraje.local', 'ADMIN', 1)
            """)
            self.conn.commit()
    
    def insertar_parametros_default(self):
        parametros = [
            ('MAX_VENTAS_DIARIAS', '3', 'INTEGER', 'OPERACION', 'Maximo de ventas por dia'),
            ('COMISION_P2P_MAKER', '0.0035', 'FLOAT', 'OPERACION', 'Comision Binance P2P'),
            ('LIMITE_FINAL_USD', '1000.00', 'FLOAT', 'OPERACION', 'Limite de capital por ciclo'),
            ('PORCENTAJE_AHORRO_BTC', '0.50', 'FLOAT', 'OPERACION', 'Porcentaje a BTC'),
        ]
        cursor = self.conn.cursor()
        for param in parametros:
            cursor.execute("""
                INSERT OR IGNORE INTO parametros_sistema 
                (nombre, valor, tipo, categoria, descripcion)
                VALUES (?, ?, ?, ?, ?)
            """, param)
        self.conn.commit()
    
    def iniciar_ciclo(self, usuario_id, dias_totales, capital_inicial, nombre_ciclo=None):
        cursor = self.conn.cursor()
        if not nombre_ciclo:
            nombre_ciclo = f"Ciclo {datetime.now().strftime('%Y-%m-%d')}"
        cursor.execute("""
            INSERT INTO ciclos (usuario_id, nombre_ciclo, fecha_inicio, dias_totales, capital_inicial, estado)
            VALUES (?, ?, ?, ?, ?, 'ACTIVO')
        """, (usuario_id, nombre_ciclo, datetime.now().date(), dias_totales, capital_inicial))
        self.conn.commit()
        return cursor.lastrowid
    
    def obtener_ciclo_activo(self, usuario_id=None):
        cursor = self.conn.cursor()
        if usuario_id:
            cursor.execute("""
                SELECT * FROM ciclos 
                WHERE usuario_id = ? AND estado = 'ACTIVO' 
                ORDER BY fecha_inicio DESC LIMIT 1
            """, (usuario_id,))
        else:
            cursor.execute("""
                SELECT * FROM ciclos 
                WHERE estado = 'ACTIVO' 
                ORDER BY fecha_inicio DESC LIMIT 1
            """)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def obtener_ultimo_dia(self, ciclo_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM dias 
            WHERE ciclo_id = ? 
            ORDER BY dia_numero DESC LIMIT 1
        """, (ciclo_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def registrar_dia(self, ciclo_id, usuario_id, dia_data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO dias (
                ciclo_id, usuario_id, dia_numero, fecha, capital_disponible_inicio,
                capital_operado, capital_no_operado, capital_fresco_inyectado,
                saldo_boveda_final, ganancia_bruta_dia, ganancia_retenida,
                ganancia_retirada, roi_dia, tipo_operacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ciclo_id, usuario_id, dia_data['dia_numero'], dia_data['fecha'],
            dia_data['capital_disponible_inicio'], dia_data['capital_operado'],
            dia_data['capital_no_operado'], dia_data['capital_fresco_inyectado'],
            dia_data['saldo_boveda_final'], dia_data['ganancia_bruta_dia'],
            dia_data['ganancia_retenida'], dia_data['ganancia_retirada'],
            dia_data['roi_dia'], dia_data['tipo_operacion']
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def registrar_venta(self, dia_id, venta_data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ventas (
                dia_id, venta_numero, monto_operado, usdt_operado,
                tasa_venta_p2p, tasa_compra, comision_monto, comision_porcentaje,
                ingreso_bruto, ingreso_neto, ganancia_venta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dia_id, venta_data['venta_numero'], venta_data['monto_operado'],
            venta_data['usdt_operado'], venta_data['tasa_venta_p2p'],
            venta_data['tasa_compra'], venta_data['comision_monto'],
            venta_data['comision_porcentaje'], venta_data['ingreso_bruto'],
            venta_data['ingreso_neto'], venta_data['ganancia_venta']
        ))
        self.conn.commit()
    
    def obtener_ventas_dia(self, dia_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ventas WHERE dia_id = ? ORDER BY venta_numero", (dia_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def log_sistema(self, nivel, modulo, funcion, mensaje, usuario_id=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO logs_sistema (nivel, modulo, funcion, mensaje, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        """, (nivel, modulo, funcion, mensaje, usuario_id))
        self.conn.commit()
    
    def cerrar(self):
        self.conn.close()

    def get_estadisticas_ciclo(self, ciclo_id):
        """Obtiene estadisticas del ciclo"""
        cursor = self.conn.cursor()
        
        # Estadisticas de dias
        cursor.execute("""
            SELECT 
                COUNT(*) as total_dias,
                COALESCE(SUM(ganancia_bruta_dia), 0) as ganancia_total,
                COALESCE(AVG(ganancia_bruta_dia), 0) as ganancia_promedio,
                COALESCE(SUM(capital_fresco_inyectado), 0) as total_inyectado
            FROM dias
            WHERE ciclo_id = ?
        """, (ciclo_id,))
        stats_dias = dict(cursor.fetchone())
        
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
        
        return {**stats_dias, **stats_ventas}

    def finalizar_ciclo(self, ciclo_id, capital_final, ganancia_total, roi_total):
        """Finaliza un ciclo"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE ciclos 
            SET fecha_fin = ?, capital_final = ?, ganancia_total = ?, 
                roi_total = ?, estado = 'FINALIZADO'
            WHERE id = ?
        """, (datetime.now().date(), capital_final, ganancia_total, roi_total, ciclo_id))
        self.conn.commit()
        self.log_sistema('INFO', 'database', 'finalizar_ciclo', f'Ciclo {ciclo_id} finalizado')
