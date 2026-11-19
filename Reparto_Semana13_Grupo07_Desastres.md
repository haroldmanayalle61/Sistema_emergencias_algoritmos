## Reparto del proyecto de la semana 13

## Grupo 07 · Distribución de ayuda humanitaria y comunicaciones de emergencia

Aplicación orientada a objetos en Python para consultar tiempos mínimos de entrega y diseñar una red de comunicaciones de inversión mínima. Este acuerdo organiza los requisitos de la guía en diez archivos principales y seis archivos de pruebas.

| Integrante | Archivos en src | Parte asignada |
| --- | --- | --- |
| Fernandito | modelo.py | Modelo, representaciones, CSV y generadores. |
|   | datos.py |   |
| Samuel | dijkstra.py | Dijkstra, rutas y análisis de accesibilidad. |
| Fernando | floyd_warshall.py | Floyd-Warshall, comparación cruzada y rendimiento. |
|   | experimento.py |   |
| Diego | prim.py | Prim y gráficos de resultados. |
|   | visualizacion.py |   |
| Harold | kruskal.py | Kruskal, conjuntos disjuntos y vulnerabilidad. |
| Garrido | sistema_emergencias.py | Integración, escenarios, exportación y menú. |
|   | main.py |   |

## Datos y objetivos comunes

- Caminos mínimos. Dijkstra y Floyd-Warshall usan tiempo_entrega_min, expresado en minutos de entrega estimado.

- Red mínima. Prim y Kruskal usan costo_enlace_miles_soles, expresado en miles de soles de enlace de emergencia.

- Instancia base. 24 vértices y 48 aristas únicas, no dirigidas, con pesos positivos. El árbol mínimo debe tener 23 aristas.

- Caso manual. Seis vértices A-F y nueve aristas. Los cuatro responsables de algoritmos deben resolverlo y explicarlo.

Organización de carpetas acordada: src/, tests/, datos/, resultados/, informe/ y presentacion/, junto con README.md y las dependencias efectivamente utilizadas.


## Acuerdos de integración y restricciones

Las clases y evidencias provienen de la guía. Las firmas, retornos y políticas de esta página son acuerdos propuestos del equipo para que los módulos coincidan al integrarse.

| Componente | Contrato común |
| --- | --- |
| Modelo | Vertice mantiene id, nombre, rol y metadatos, con igualdad por id. Arista mantiene origen, |
|   | destino, peso_ruta y peso_red. Grafo conserva ambos pesos sin mezclarlos. |
| Grafo | Operaciones acordadas: agregar_vertice, eliminar_vertice, agregar_arista, eliminar_arista, |
|   | vecinos, vertices, aristas, copiar, es_conexo, a_lista_adyacencia y a_matriz_adyacencia. |
|   | vecinos(id) entrega pares (id_vecino, Arista). |
| Representaciones | Las consultas de representación reciben la métrica peso_ruta o peso_red. La matriz devuelve |
|   | también el orden de ids. Diagonal 0, ausencia de conexión infinito y simetría. |
| Dijkstra(grafo) | calcular_desde(origen) devuelve (distancias, predecesores), diccionarios por id. |
|   | reconstruir_camino(destino) devuelve lista de ids o None. Requiere un cálculo previo. |
| FloydWarshall(grafo) | calcular_todos() devuelve (matriz_distancias, matriz_siguiente). Expone el orden de ids. |
|   | reconstruir_camino(origen, destino) devuelve lista de ids o None. |
| Prim(grafo) y | calcular_arbol(inicio) en Prim y calcular_arbol() en Kruskal devuelven (lista de Arista, |
| Kruskal(grafo) | costo_total). En un grafo desconectado devuelven un bosque que el sistema identifica |
|   | explícitamente. |
| ConjuntosDisjuntos | Inicializa un conjunto por id. find(id) obtiene representante. union(a, b) devuelve True si unió |
|   | grupos y False si ya estaban unidos. Incluye compresión y rango o tamaño. |

## Reglas para todos

- Algoritmos propios. Se permiten heapq, csv, random, statistics y time. NetworkX puede apoyar dibujo o validación independiente según LEEME; los resultados evaluados salen de las implementaciones del equipo.

- IDs desconocidos generan KeyError. Duplicados o datos incompatibles generan ValueError; tipos incorrectos, TypeError. La carga exige pesos positivos y finitos, en concordancia con los datos base.

- Una conexión no dirigida se consulta en ambos sentidos y se enumera una sola vez para Kruskal. Al eliminar un vértice se retiran todas sus conexiones.

- Las copias son independientes. Tras un cambio se recalculan los resultados. Las trazas son opcionales y se desactivan durante las mediciones.


## Fernandito y Samuel

## 1. Fernandito · Modelo y datos

Archivos. modelo.py, datos.py y tests/test_modelo.py.

- Implementar Vertice, Arista y Grafo, con atributos encapsulados e interfaces de la página anterior. Conservar los objetos del dominio y localizar vértices mediante diccionarios por id.

- Entregar lista y matriz de adyacencia para cada métrica, conectividad, consulta de pesos, altas, bajas y copia independiente del escenario.

- Cargar vertices.csv y aristas.csv. Detectar campos faltantes, valores no numéricos, ids desconocidos, duplicados inversos y pesos inválidos. Informar archivo y fila del error.

- Adaptar los encabezados de grafo_manual.csv y crear sus vértices A-F a partir de los extremos. Conservar el campo tipo original en los metadatos.

- Generar grafos conectados y reproducibles de 100 y 200 vértices, dispersos y densos, con semilla fija y ambos pesos positivos. Coordinar sus parámetros con Fernando.

- Comprobar 24 vértices, 48 conexiones únicas, simetría y conectividad. Probar también eliminación de vértices, copias y errores de entrada.

Evidencia. P1 y validaciones de P7; explicación de estructuras y unidades. Coordina el UML general con las clases y firmas que cada autor le entregue.

## 2. Samuel · Dijkstra y accesibilidad

Archivos. dijkstra.py y tests/test_dijkstra.py.

- Implementar Dijkstra con heapq y lista de adyacencia, distancias y predecesores. Gestionar entradas antiguas del heap y rutas inexistentes.

- Ejecutar desde N02 y N03 hacia N06, N10, N14 y N20. Entregar las ocho rutas completas y sus tiempos acumulados.

- Desde N02 comparar los tiempos mínimos a los albergues N06-N10 y señalar los más alejados, incluidos empates.

- Resolver manualmente desde A. Registrar extracciones, relajaciones, distancias tentativas y predecesores; reconstruir A-F.

- Preparar tablas de rutas y tiempos antes/después para que Garrido las integre. Separar destinos inalcanzables de aumentos finitos.

Evidencia. Aporta a P2, P3, P5, P7 y P9. Explica O((V+E) log V) con heap y adyacencia, y la memoria utilizada.


## Fernando y Diego

## 3. Fernando · Floyd-Warshall y experimentos

Archivos. floyd_warshall.py, experimento.py y tests/test_floyd_warshall.py.

- Implementar matrices de distancias y siguiente vértice. Mantener correspondencia entre índices e ids. Reconstruir rutas y devolver None para pares inalcanzables.

- Obtener todos los pares del grafo base y comparar con Dijkstra ejecutado desde cada uno de los 24 orígenes. Verificar continuidad y suma de rutas, sin exigir el mismo camino cuando haya empate.

- En el caso A-F documentar la matriz inicial, dos iteraciones intermedias explicadas, matriz final y consulta A-F. Poder registrar las iteraciones por vértice intermedio.

- Medir los cuatro algoritmos sobre la base de 24 vértices y cuatro configuraciones sintéticas: 100 disperso, 100 denso, 200 disperso y 200 denso.

- Usar perf_counter, cinco o más repeticiones, mediana, semilla fija y registro de entorno, V, E y E/V. Excluir lectura, dibujos, impresión y trazas del tiempo medido.

- Medir Dijkstra desde una fuente y, para comparar la tarea de todos los pares, también desde todos los orígenes. Indicar qué trabajo produce cada medición.

Evidencia. P2, P3 y P8; tablas y análisis empírico. Justifica Floyd-Warshall en O(V³) tiempo y O(V²) memoria. El generador se reutiliza desde datos.py.

## 4. Diego · Prim y visualización

Archivos. prim.py, visualizacion.py y tests/test_prim.py.

- Implementar Prim con peso_red y heap de candidatos. Elegir conexiones que incorporan vértices fuera del árbol y descartar candidatos que crearían ciclos.

- Ejecutar desde N02 y N03. Informar conexiones, costo, cobertura y 23 aristas en el grafo base. En desconexión continuar por componentes y señalar bosque.

- Resolver el caso manual desde A con frontera, arista elegida, vértice añadido y costo acumulado. Coordinar pruebas de empates con Harold.

- Dibujar los 24 nodos y 48 conexiones usando coordenadas esquemáticas. Producir grafo inicial, rutas, árboles y al menos una figura antes/después.

- Mantener legibles las etiquetas. Cada figura declara la métrica usada, sus unidades y el significado de los elementos resaltados.

Evidencia. Prim en P4 y P6, visualizaciones y complejidad de su variante. Explica heap, frontera y memoria; justifica la cota según la implementación real.


## Harold y Garrido

## 5. Harold · Kruskal y conjuntos disjuntos

Archivos. kruskal.py y tests/test_kruskal.py. Las dos clases van en el mismo módulo.

- Implementar ConjuntosDisjuntos con un grupo inicial por vértice, find con compresión de caminos y union por rango o tamaño.

- Implementar Kruskal ordenando conexiones únicas por peso_red. Aceptar una arista cuando une componentes distintas y rechazarla si forma un ciclo.

- Entregar aristas seleccionadas, costo y cobertura. En el caso base obtener 23 aristas y comparar el costo con Prim; en desconexión identificar un bosque.

- Resolver las nueve aristas del caso manual con orden, representantes, aceptación o rechazo y costo acumulado. En la evidencia pedagógica clasificar también las aristas restantes cuando el árbol ya se haya completado.

- Analizar una falla en una copia del MST: identificar la arista retirada y los dos grupos separados. Explicar las instalaciones afectadas y buscar enlaces alternativos en el grafo completo.

- Preparar la tabla y explicación de vulnerabilidad para que Garrido las incorpore al sistema. Coordinar con Diego pruebas de costos, empates, ausencia de ciclos y cobertura.

Evidencia. Kruskal en P4-P6 y análisis de vulnerabilidad. Explica O(E log E), costo amortizado de Union-Find y memoria.

## 6. Garrido · Sistema de Emergencias e integración

Archivos. sistema_emergencias.py, main.py y tests/test_integracion.py.

- Implementar SistemaEmergencias para coordinar carga, consultas, algoritmos, resultados, escenarios y exportación. main.py contiene menú y entrada del programa.

- Reutilizar las implementaciones de cada compañero. Mostrar consultas de rutas, matrices, árboles, trazas manuales, accesibilidad y vulnerabilidad.

- Crear una copia del original, retirar simultáneamente N02-N08 y N15-N21 y recalcular los cuatro algoritmos. Exportar los datos modificados y una tabla antes/después.

- Mostrar rutas y tiempos afectados, pares inaccesibles, cantidad de componentes, aristas del árbol y costo total. Conservar identificadas la base y la copia.

- Integrar las pruebas P1-P9. Preparar una modificación de enlace o peso para la demostración, README y ejecución reproducible.

Evidencia. P5, P7 y P9 a nivel de sistema y coordinación del resto. Cada autor corrige los fallos de su propio módulo.


## Pruebas y entregables verificables

| Prueba | Responsables | Evidencia mínima |
| --- | --- | --- |
| P1 Modelo | Fernandito; Garrido | 24 nodos, 48 aristas únicas, simetría, pesos positivos y conectividad. |
|   | integra |   |
| P2 Distancias | Samuel y Fernando | Dijkstra y Floyd coinciden para todos los pares del grafo base. |
| P3 Rutas | Samuel y Fernando | Continuidad, extremos correctos y suma igual a la distancia. Casos |
|   |   | inalcanzables y origen igual a destino. |
| P4 Árboles | Diego y Harold | Cobertura de 24 nodos, 23 aristas, sin ciclos, conectividad e igualdad de |
|   |   | costos Prim/Kruskal. |
| P5 | Garrido con los cuatro | Aislar un vértice en otra copia. Infinito/None en caminos y bosque |
| Desconexión | autores | identificado en expansión mínima. |
| P6 Empates | Diego y Harold | Caso con pesos iguales. Demostrar costo óptimo coincidente aunque |
|   |   | pueda haber árboles distintos. |
| P7 Errores | Fernandito y Garrido | CSV defectuoso, datos faltantes, ids desconocidos y pesos negativos; |
|   |   | algoritmos prueban sus entradas públicas. |
| P8 Escala | Fernando y Fernandito | 24, 100 y 200 nodos; dispersos y densos, E/V, semilla, cinco |
|   |   | repeticiones, mediana y entorno. |
| P9 Desastre | Garrido con Samuel, | Dos eliminaciones exactas, base intacta, recálculo y tabla antes/después |
|   | Fernando, Diego y Harold | con interpretación. |

## Informe y presentación

Cada integrante entrega su sección redactada, fragmentos de código, pruebas, traza manual cuando corresponda, complejidad, resultados y diapositivas. Fernando consolida el informe; los seis revisan contenido y fuentes académicas o técnicas en APA 7. Fernandito coordina el UML y Garrido la demostración funcional.

## Preguntas que deben quedar respondidas

Albergues más alejados de N02; aumento de rutas tras los cierres; pares inaccesibles; red de radio más económica; vulnerabilidad ante una falla del MST; diferencia entre camino mínimo y árbol mínimo; efecto de la representación; límites del modelo para decisiones reales.

## Interpretación de los escenarios

La revisión de los CSV confirma que el cierre obligatorio deja 46 aristas y mantiene conectados los 24 nodos. Debe verificarse de nuevo con el programa. No se debe inventar una pérdida de accesibilidad: una red conectada puede sufrir aumentos de tiempo y cambios de costo. El caso P5 se prepara por separado.

Los datos son sintéticos. El modelo no incluye demanda, prioridades humanitarias, capacidad de caminos ni incertidumbre. El reto de añadir una conexión estratégica es una ampliación posterior al núcleo obligatorio.


## Orden de trabajo y revisión cruzada

| Etapa | Quiénes trabajan en paralelo | Resultado que habilita la siguiente etapa |
| --- | --- | --- |
| 1. Contrato | Los seis. Fernandito coordina modelo; Garrido, | Firmas y retornos de la página 2 acordados; |
|   | integración. | ubicación de CSV y estructura de resultados |
|   |   | definidas. |
| 2. Construc | Fernandito desarrolla modelo y datos. Samuel, | Carga validada, grafo manual disponible y |
| ción | Fernando, Diego y Harold avanzan sus algoritmos con | primera ejecución de cada módulo. Se pueden |
|   | el caso A-F. Garrido prepara sistema y menú con esas | usar objetos mínimos de prueba que respeten |
|   | interfaces. | el contrato. |
| 3. Compara | Samuel + Fernando comparan caminos. Diego + Harold | Distancias coincidentes, costos mínimos |
| ción | comparan árboles. Fernandito + Garrido revisan | coincidentes e integración reproducible de los |
|   | modelo, errores, copias y escenario. | datos base. |
| 4. | Fernando mide rendimiento; Diego prepara gráficos; | P1-P9, trazas, figuras y tablas antes/después |
| Evidencias | Samuel prepara accesibilidad; Harold analiza | completas. |
|   | vulnerabilidad; Fernandito cierra UML y datos; Garrido |   |
|   | ejecuta integración. |   |
| 5. Entrega | Todos entregan sus secciones. Fernando consolida | Código, datos, pruebas, resultados, informe, |
|   | informe. Garrido organiza demo. Cada autor valida su | UML, presentación y README coherentes |
|   | sección y sus diapositivas. | entre sí. |

## Revisión entre compañeros

| Revisor | Parte que revisa |
| --- | --- |
| Fernandito | Samuel · Dijkstra y rutas |
| Samuel | Fernando · Floyd y experimentos |
| Fernando | Diego · Prim y visualización |
| Diego | Harold · Kruskal y Union-Find |
| Harold | Garrido · Sistema, escenario y menú |
| Garrido | Fernandito · Modelo y carga |

## Cobertura de la rúbrica de 20 puntos

Análisis y modelado (3): Fernandito y todos en interpretación. POO y UML (3): Fernandito coordina; todos aportan. Dijkstra (2): Samuel. Floyd (2): Fernando. Prim (2): Diego. Kruskal y Union-Find (2): Harold. Pruebas, complejidad y comparación (3): Fernando y Garrido coordinan con cada autor. Interpretación y sustentación (3): los seis.

Cada integrante debe explicar también los dos objetivos, unidades, resultado de los cuatro algoritmos y límites del modelo. La defensa individual y una modificación en vivo forman parte de la guía.
