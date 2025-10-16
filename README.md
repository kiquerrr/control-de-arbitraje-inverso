?? CONTROL DE ARBITRAJE INVERSO P2P (USDT/USD)Este proyecto en Python proporciona una herramienta de control de gesti�n dise�ada para rastrear la rentabilidad diaria de una estrategia de arbitraje inverso Peer-to-Peer (P2P) en Binance, utilizando la compra de USDT con tarjeta bancaria (Facebank u otras) como punto de entrada.El objetivo principal es maximizar la ganancia neta diaria mientras se respeta un l�mite de capital bancario autoimpuesto, controlando el inter�s compuesto diario y la reinversi�n.?? CONTEXTO DEL NEGOCIO Y OPORTUNIDADEl an�lisis de mercado identific� una disparidad significativa entre el Costo de Adquisici�n de USDT (compra directa con tarjeta) y el Precio de Venta de USDT en el mercado P2P.An�lisis de Rentabilidad BaseM�tricaCosto Real (Tarjeta)Tasa de Venta P2P (Ejemplo)Rentabilidad por CicloUSD por 1 USDT1.04424 USD1.12895 USD7.74%Comisi�n P2P MakerN/A0.35%N/AEstrategia de Arbitraje Inverso:Compra Barata (Entrada): Comprar USDT con tarjeta a 1.04424 USD/USDT.Venta Cara (Salida): Publicar un anuncio P2P para vender ese USDT a una tasa competitiva ($\geq 1.0479 \text{ USD}/\text{USDT}$).?? FASE 1: AVANCE DEL PROYECTO (COMPLETADO)Se ha completado la l�gica base para el control diario, encapsulada en dos archivos principales.Estructura del SoftwareArchivoRolDescripci�narbitraje_core.pyL�gica del NegocioContiene la clase CicloArbitraje con las f�rmulas de c�lculo de rentabilidad, la gesti�n de comisiones y la l�gica de inter�s compuesto por ciclos.main.pyControl OperativoScript ejecutable que gestiona el flujo de 5 pasos, solicita datos din�micos, carga/guarda el estado de la B�veda y registra las transacciones en historico_arbitraje.csv.data/config_ciclo.txtEstadoAlmacena el SALDO de la B�veda, los DIAS restantes y el CAPITAL_INICIAL_GLOBAL para la continuidad del ciclo.Flujo Operativo Diario ImplementadoEl operador ejecuta python3 main.py y sigue estos 5 pasos, con el sistema ajustando los costos y registrando el impacto:PASO 1: Inyectar Capital USD (Compra con Tarjeta).PASO 2: Ingresar el Costo USDT/Tarjeta de la adquisici�n.PASO 3: Publicar Tasa de Venta P2P (El sistema sugiere la tasa �ptima basada en el 2% de competitividad).PASO 4: Registrar Ciclos Completados (1 a 3).PASO 5: Decidir Retiro/Reinversi�n de la ganancia.?? FUTURO Y ESCALABILIDAD (FASE 3)La siguiente etapa se centrar� en eliminar la entrada manual de datos para crear un sistema de arbitraje semi-autom�tico.HitoDescripci�nImpacto3.1 Integraci�n API de BinanceConectar el script a la API de Binance para obtener las tasas de compra/venta en tiempo real, eliminando la entrada manual de PASO 2 y PASO 3a.Mayor precisi�n y rapidez operativa.3.2 M�ltiples MonedasAdaptar la clase CicloArbitraje para manejar diferentes pares (Ej: USDT/EUR) o diferentes m�todos bancarios con sus propias comisiones.Expansi�n del negocio.3.3 Reporte Gr�fico y An�lisisUso de la librer�a pandas y matplotlib para generar gr�ficos de rendimiento, volumen y an�lisis de spread hist�rico.An�lisis de decisiones y optimizaci�n del timing.??? INSTRUCCIONES DE USOActivaci�n: Aseg�rese de estar en el directorio arbitraje_p2p_control con el entorno virtual (venv) activo.Ejecuci�n: Inicie la operaci�n: python3 main.pyLimpieza (Inicio de un Ciclo Nuevo): Si el ciclo actual ha terminado (o desea reiniciar el D�a 1), elimine el archivo de estado: rm -f data/config_ciclo.txt.?? CONTROL DE ARBITRAJE INVERSO P2P (USDT/USD)

Este proyecto en Python proporciona una herramienta de control de gesti�n dise�ada para rastrear la rentabilidad diaria de una estrategia de arbitraje inverso Peer-to-Peer (P2P) en Binance, utilizando la compra de USDT con tarjeta bancaria (Facebank u otras) como punto de entrada.

El objetivo principal es maximizar la ganancia neta diaria mientras se respeta un l�mite de capital bancario autoimpuesto, controlando el inter�s compuesto diario y la reinversi�n.

?? CONTEXTO DEL NEGOCIO Y OPORTUNIDAD

El an�lisis de mercado identific� una disparidad significativa entre el Costo de Adquisici�n de USDT (compra directa con tarjeta) y el Precio de Venta de USDT en el mercado P2P.

An�lisis de Rentabilidad Base

|

| M�trica | Costo Real (Tarjeta) | Tasa de Venta P2P (Ejemplo) | Rentabilidad por Ciclo |
| USD por 1 USDT | 1.04424 USD | 1.12895 USD | 7.74% |
| Comisi�n P2P Maker | N/A | 0.35% | N/A |

Estrategia de Arbitraje Inverso:

Compra Barata (Entrada): Comprar USDT con tarjeta a 1.04424 USD/USDT.

Venta Cara (Salida): Publicar un anuncio P2P para vender ese USDT a una tasa competitiva ($\geq 1.0479 \text{ USD}/\text{USDT}$).

?? FASE 1: AVANCE DEL PROYECTO (COMPLETADO)

Se ha completado la l�gica base para el control diario, encapsulada en dos archivos principales.

Estructura del Software

| Archivo | Rol | Descripci�n |
| arbitraje_core.py | L�gica del Negocio | Contiene la clase CicloArbitraje con las f�rmulas de c�lculo de rentabilidad, la gesti�n de comisiones y la l�gica de inter�s compuesto por ciclos. |
| main.py | Control Operativo | Script ejecutable que gestiona el flujo de 5 pasos, solicita datos din�micos, carga/guarda el estado de la B�veda y registra las transacciones en historico_arbitraje.csv. |
| data/config_ciclo.txt | Estado | Almacena el SALDO de la B�veda, los DIAS restantes y el CAPITAL_INICIAL_GLOBAL para la continuidad del ciclo. |

Flujo Operativo Diario Implementado

El operador ejecuta python3 main.py y sigue estos 5 pasos, con el sistema ajustando los costos y registrando el impacto:

PASO 1: Inyectar Capital USD (Compra con Tarjeta).

PASO 2: Ingresar el Costo USDT/Tarjeta de la adquisici�n.

PASO 3: Publicar Tasa de Venta P2P (El sistema sugiere la tasa �ptima basada en el 2% de competitividad).

PASO 4: Registrar Ciclos Completados (1 a 3).

PASO 5: Decidir Retiro/Reinversi�n de la ganancia.

?? FUTURO Y ESCALABILIDAD (FASE 3)

La siguiente etapa se centrar� en eliminar la entrada manual de datos para crear un sistema de arbitraje semi-autom�tico.

| Hito | Descripci�n | Impacto |
| 3.1 Integraci�n API de Binance | Conectar el script a la API de Binance para obtener las tasas de compra/venta en tiempo real, eliminando la entrada manual de PASO 2 y PASO 3a. | Mayor precisi�n y rapidez operativa. |
| 3.2 M�ltiples Monedas | Adaptar la clase CicloArbitraje para manejar diferentes pares (Ej: USDT/EUR) o diferentes m�todos bancarios con sus propias comisiones. | Expansi�n del negocio. |
| 3.3 Reporte Gr�fico y An�lisis | Uso de la librer�a pandas y matplotlib para generar gr�ficos de rendimiento, volumen y an�lisis de spread hist�rico. | An�lisis de decisiones y optimizaci�n del timing. |

??? INSTRUCCIONES DE USO

Activaci�n: Aseg�rese de estar en el directorio arbitraje_p2p_control con el entorno virtual (venv) activo.

Ejecuci�n: Inicie la operaci�n: python3 main.py

Limpieza (Inicio de un Ciclo Nuevo): Si el ciclo actual ha terminado (o desea reiniciar el D�a 1), elimine el archivo de estado: rm -f data/config_ciclo.txt.