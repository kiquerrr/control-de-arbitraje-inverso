?? CONTROL DE ARBITRAJE INVERSO P2P (USDT/USD)Este proyecto en Python proporciona una herramienta de control de gestión diseñada para rastrear la rentabilidad diaria de una estrategia de arbitraje inverso Peer-to-Peer (P2P) en Binance, utilizando la compra de USDT con tarjeta bancaria (Facebank u otras) como punto de entrada.El objetivo principal es maximizar la ganancia neta diaria mientras se respeta un límite de capital bancario autoimpuesto, controlando el interés compuesto diario y la reinversión.?? CONTEXTO DEL NEGOCIO Y OPORTUNIDADEl análisis de mercado identificó una disparidad significativa entre el Costo de Adquisición de USDT (compra directa con tarjeta) y el Precio de Venta de USDT en el mercado P2P.Análisis de Rentabilidad BaseMétricaCosto Real (Tarjeta)Tasa de Venta P2P (Ejemplo)Rentabilidad por CicloUSD por 1 USDT1.04424 USD1.12895 USD7.74%Comisión P2P MakerN/A0.35%N/AEstrategia de Arbitraje Inverso:Compra Barata (Entrada): Comprar USDT con tarjeta a 1.04424 USD/USDT.Venta Cara (Salida): Publicar un anuncio P2P para vender ese USDT a una tasa competitiva ($\geq 1.0479 \text{ USD}/\text{USDT}$).?? FASE 1: AVANCE DEL PROYECTO (COMPLETADO)Se ha completado la lógica base para el control diario, encapsulada en dos archivos principales.Estructura del SoftwareArchivoRolDescripciónarbitraje_core.pyLógica del NegocioContiene la clase CicloArbitraje con las fórmulas de cálculo de rentabilidad, la gestión de comisiones y la lógica de interés compuesto por ciclos.main.pyControl OperativoScript ejecutable que gestiona el flujo de 5 pasos, solicita datos dinámicos, carga/guarda el estado de la Bóveda y registra las transacciones en historico_arbitraje.csv.data/config_ciclo.txtEstadoAlmacena el SALDO de la Bóveda, los DIAS restantes y el CAPITAL_INICIAL_GLOBAL para la continuidad del ciclo.Flujo Operativo Diario ImplementadoEl operador ejecuta python3 main.py y sigue estos 5 pasos, con el sistema ajustando los costos y registrando el impacto:PASO 1: Inyectar Capital USD (Compra con Tarjeta).PASO 2: Ingresar el Costo USDT/Tarjeta de la adquisición.PASO 3: Publicar Tasa de Venta P2P (El sistema sugiere la tasa óptima basada en el 2% de competitividad).PASO 4: Registrar Ciclos Completados (1 a 3).PASO 5: Decidir Retiro/Reinversión de la ganancia.?? FUTURO Y ESCALABILIDAD (FASE 3)La siguiente etapa se centrará en eliminar la entrada manual de datos para crear un sistema de arbitraje semi-automático.HitoDescripciónImpacto3.1 Integración API de BinanceConectar el script a la API de Binance para obtener las tasas de compra/venta en tiempo real, eliminando la entrada manual de PASO 2 y PASO 3a.Mayor precisión y rapidez operativa.3.2 Múltiples MonedasAdaptar la clase CicloArbitraje para manejar diferentes pares (Ej: USDT/EUR) o diferentes métodos bancarios con sus propias comisiones.Expansión del negocio.3.3 Reporte Gráfico y AnálisisUso de la librería pandas y matplotlib para generar gráficos de rendimiento, volumen y análisis de spread histórico.Análisis de decisiones y optimización del timing.??? INSTRUCCIONES DE USOActivación: Asegúrese de estar en el directorio arbitraje_p2p_control con el entorno virtual (venv) activo.Ejecución: Inicie la operación: python3 main.pyLimpieza (Inicio de un Ciclo Nuevo): Si el ciclo actual ha terminado (o desea reiniciar el Día 1), elimine el archivo de estado: rm -f data/config_ciclo.txt.?? CONTROL DE ARBITRAJE INVERSO P2P (USDT/USD)

Este proyecto en Python proporciona una herramienta de control de gestión diseñada para rastrear la rentabilidad diaria de una estrategia de arbitraje inverso Peer-to-Peer (P2P) en Binance, utilizando la compra de USDT con tarjeta bancaria (Facebank u otras) como punto de entrada.

El objetivo principal es maximizar la ganancia neta diaria mientras se respeta un límite de capital bancario autoimpuesto, controlando el interés compuesto diario y la reinversión.

?? CONTEXTO DEL NEGOCIO Y OPORTUNIDAD

El análisis de mercado identificó una disparidad significativa entre el Costo de Adquisición de USDT (compra directa con tarjeta) y el Precio de Venta de USDT en el mercado P2P.

Análisis de Rentabilidad Base

|

| Métrica | Costo Real (Tarjeta) | Tasa de Venta P2P (Ejemplo) | Rentabilidad por Ciclo |
| USD por 1 USDT | 1.04424 USD | 1.12895 USD | 7.74% |
| Comisión P2P Maker | N/A | 0.35% | N/A |

Estrategia de Arbitraje Inverso:

Compra Barata (Entrada): Comprar USDT con tarjeta a 1.04424 USD/USDT.

Venta Cara (Salida): Publicar un anuncio P2P para vender ese USDT a una tasa competitiva ($\geq 1.0479 \text{ USD}/\text{USDT}$).

?? FASE 1: AVANCE DEL PROYECTO (COMPLETADO)

Se ha completado la lógica base para el control diario, encapsulada en dos archivos principales.

Estructura del Software

| Archivo | Rol | Descripción |
| arbitraje_core.py | Lógica del Negocio | Contiene la clase CicloArbitraje con las fórmulas de cálculo de rentabilidad, la gestión de comisiones y la lógica de interés compuesto por ciclos. |
| main.py | Control Operativo | Script ejecutable que gestiona el flujo de 5 pasos, solicita datos dinámicos, carga/guarda el estado de la Bóveda y registra las transacciones en historico_arbitraje.csv. |
| data/config_ciclo.txt | Estado | Almacena el SALDO de la Bóveda, los DIAS restantes y el CAPITAL_INICIAL_GLOBAL para la continuidad del ciclo. |

Flujo Operativo Diario Implementado

El operador ejecuta python3 main.py y sigue estos 5 pasos, con el sistema ajustando los costos y registrando el impacto:

PASO 1: Inyectar Capital USD (Compra con Tarjeta).

PASO 2: Ingresar el Costo USDT/Tarjeta de la adquisición.

PASO 3: Publicar Tasa de Venta P2P (El sistema sugiere la tasa óptima basada en el 2% de competitividad).

PASO 4: Registrar Ciclos Completados (1 a 3).

PASO 5: Decidir Retiro/Reinversión de la ganancia.

?? FUTURO Y ESCALABILIDAD (FASE 3)

La siguiente etapa se centrará en eliminar la entrada manual de datos para crear un sistema de arbitraje semi-automático.

| Hito | Descripción | Impacto |
| 3.1 Integración API de Binance | Conectar el script a la API de Binance para obtener las tasas de compra/venta en tiempo real, eliminando la entrada manual de PASO 2 y PASO 3a. | Mayor precisión y rapidez operativa. |
| 3.2 Múltiples Monedas | Adaptar la clase CicloArbitraje para manejar diferentes pares (Ej: USDT/EUR) o diferentes métodos bancarios con sus propias comisiones. | Expansión del negocio. |
| 3.3 Reporte Gráfico y Análisis | Uso de la librería pandas y matplotlib para generar gráficos de rendimiento, volumen y análisis de spread histórico. | Análisis de decisiones y optimización del timing. |

??? INSTRUCCIONES DE USO

Activación: Asegúrese de estar en el directorio arbitraje_p2p_control con el entorno virtual (venv) activo.

Ejecución: Inicie la operación: python3 main.py

Limpieza (Inicio de un Ciclo Nuevo): Si el ciclo actual ha terminado (o desea reiniciar el Día 1), elimine el archivo de estado: rm -f data/config_ciclo.txt.