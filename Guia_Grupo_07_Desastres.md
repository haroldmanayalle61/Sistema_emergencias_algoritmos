**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

### **TRABAJO APLICATIVO · GRUPO 07** 

# **Distribución de ayuda humanitaria y comunicaciones de emergencia** 

_Accesibilidad de puntos críticos y conectividad operativa mínima_ 

|**Curso**|**Modalidad**|**Lenguaje**|
|---|---|---|
|Estructura de Datos Orientada a Objetos|Grupal · Evaluación integradora|Python 3 · POO|



**Documento para estudiantes. No incluye implementaciones ni respuestas de los algoritmos.** 

## **01  Presentación y contexto** 

Una agencia de gestión de riesgos coordina almacenes humanitarios, albergues, zonas de evacuación y centros de mando en un escenario simulado. Los corredores de acceso tienen tiempos de reparto y costos distintos para desplegar enlaces de comunicación de campo. 

Tras un evento extremo pueden perderse dos corredores simultáneamente. La agencia necesita justificar la accesibilidad restante y un plan básico de comunicaciones. 

## **02  Problema a resolver** 

Construir una aplicación que permita consultar caminos mínimos según la métrica «minutos de entrega estimado», obtener la matriz de rutas entre todas las instalaciones y calcular una red conexa de menor inversión en miles de soles de enlace de emergencia. Se deben distinguir los objetivos matemáticos, mostrar los resultados y justificar técnicamente los cuatro algoritmos. 

## **03  Objetivos académicos** 

Objetivo general. Diseñar, implementar y evaluar una aplicación orientada a objetos que resuelva los dos subproblemas de optimización del caso utilizando Dijkstra, Floyd-Warshall, Prim y Kruskal. 

- Formalizar la red como un grafo no dirigido, ponderado y conexo de 24 vértices y 48 aristas. 

- Implementar las dos representaciones habituales y documentar sus ventajas y limitaciones. 

- Programar los cuatro algoritmos sin invocar implementaciones externas que resuelvan el problema. 

- Validar la corrección mediante trazas manuales, pruebas automatizadas y comparación cruzada. 

- Evaluar complejidad, rendimiento, escenarios de cambio y resultados de negocio. 

## **04  Datos, dominio y restricciones** 

|**Propiedad**|**Especificación**|
|---|---|
|Modelo base|Grafo no dirigido con pesos positivos y simétricos.|
|Volumen|24 vértices y 48 aristas únicas; datos sintéticos.|
|Peso de caminos|tiempo_entrega_min · minutos de entrega estimado.|
|Peso de red|costo_enlace_miles_soles · miles de soles de enlace de emergencia.|
|Alcance Dijkstra|Fuente única; consultar rutas y costos a múltiples destinos.|
|Alcance Floyd-<br>Warshall|Todos los pares; reconstrucción de rutas.|
|Alcance Prim/Kruskal|Árbol de expansión mínima de 24 vértices; 23 aristas en la instancia<br>base.|
|Datos de prueba|CSV de 24 nodos, CSV de 48 aristas y CSV manual de 6 nodos/9 aristas.|



_Advertencia de modelado. Los pesos de caminos y de instalación responden a objetivos distintos; no deben intercambiarse. Las coordenadas x_esquema e y_esquema son únicamente para visualización, no localizaciones reales._ 

Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 1 

**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

## **05  Catálogo de vértices** 

|**ID**|**Instalación**|**ID**|**Instalación**|
|---|---|---|---|
|N01|Centro de Mando|N13|Zona Evacuación C|
|N02|Almacén Humanitario<br>Norte|N14|Zona Evacuación D|
|N03|Almacén Humanitario Sur|N15|Punto Médico A|
|N04|Almacén Humanitario Este|N16|Punto Médico B|
|N05|Almacén Humanitario<br>Oeste|N17|Punto Médico C|
|N06|Albergue Central|N18|Punto de Agua A|
|N07|Albergue Norte|N19|Punto de Agua B|
|N08|Albergue Sur|N20|Punto de Agua C|
|N09|Albergue Río|N21|Puente Norte|
|N10|Albergue Montaña|N22|Puente Sur|
|N11|Zona Evacuación A|N23|Estación Radio|
|N12|Zona Evacuación B|N24|Centro de<br>Coordinación|



## **06  Catálogo de aristas y pesos** 

El archivo aristas.csv contiene todas las conexiones no dirigidas. La tabla incluye los 48 corredores candidatos del problema; las cifras son sintéticas, positivas y están expresadas en las unidades indicadas en la sección 04. 

|**Arista**|**Ruta**|**Red**|**Arista**|**Ruta**|**Red**|
|---|---|---|---|---|---|
|N01–N02|20|52|N10–N16|23|44|
|N01–N07|19|55|N11–N12|23|69|
|N01–N08|30|75|N11–N17|18|47|
|N02–N03|22|39|N12–N18|19|32|
|N02–N08|21|42|N12–N24|36|91|
|N03–N04|27|75|N13–N14|18|33|
|N03–N07|40|94|N13–N19|18|47|
|N03–N08|23|51|N14–N15|28|61|
|N03–N09|16|48|N14–N20|21|43|
|N04–N05|22|56|N15–N16|18|45|
|N04–N10|24|48|N15–N20|32|75|
|N05–N06|25|51|N15–N21|24|47|
|N05–N11|23|43|N16–N17|24|50|
|N06–N12|23|53|N16–N22|18|50|
|N06–N17|38|84|N17–N18|15|32|
|N07–N08|21|60|N17–N23|19|55|
|N07–N09|38|96|N18–N22|39|113|
|N07–N13|25|48|N18–N23|29|59|
|N08–N09|21|44|N18–N24|22|72|
|N08–N14|27|57|N19–N20|16|51|
|N09–N10|19|53|N20–N21|17|37|
|N09–N15|27|70|N21–N22|23|67|
|N09–N16|25|75|N22–N23|21|44|
|N10–N11|16|43|N23–N24|26|55|



## **07  Consultas obligatorias del caso** 

### **7.1. Optimización de caminos: Dijkstra y Floyd-Warshall** 

1.  ¿Qué albergues quedan más alejados, en tiempo mínimo, del Almacén Norte? 

2.  ¿Cuánto aumenta la mejor ruta al quedar inhabilitados dos corredores? 

3.  ¿Qué pares de instalaciones quedan inaccesibles, si los hay? 

Para Dijkstra, usar como orígenes obligatorios N02 y N03. Informar rutas completas hacia N06, N10, N14, N20 y su peso de ruta acumulado. En Floyd-Warshall, obtener todos los pares y contrastar como mínimo esas consultas. 

### **7.2. Diseño de red: Prim y Kruskal** 

1.  ¿Cuál es la red de radio de despliegue más económico antes del desastre? 

Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 2 

**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

#### 2.  ¿Qué puntos quedarían vulnerables si se pierde una arista del MST? 

Presentar lista de aristas seleccionadas, suma total del peso de red, número de aristas y verificación de conectividad. Cuando existan empates, explicar por qué pueden aparecer árboles distintos de igual costo óptimo. 

## **08  Actividades y procedimiento de desarrollo** 

### **Etapa A. Comprensión y especificación** 

1.  Formular el problema con sus propias palabras: qué se minimiza en cada subproblema, quién usará el resultado y cuáles son las restricciones. 

2.  Indicar expresamente que tiempo_entrega_min está expresado en minutos de entrega estimado y que costo_enlace_miles_soles se expresa en miles de soles de enlace de emergencia. No sumarlos ni compararlos entre sí. 

3.  Establecer entradas, salidas, supuestos, decisiones y riesgos de una optimización basada en datos sintéticos. 

### **Etapa B. Modelado y representaciones** 

1.  Construir dos vistas del mismo grafo no dirigido y conexo: caminos mínimos con peso_ruta y árbol de expansión mínima con peso_red. 

2.  Implementar lista de adyacencia y matriz de adyacencia; representar correctamente diagonal cero, ausencia de conexión y simetría. 

3.  Visualizar los 24 vértices, 48 aristas, pesos, rutas y árboles. Justificar las decisiones de diseño de datos. 

### **Etapa C. POO y arquitectura** 

1.  Elaborar UML de clases con responsabilidades y relaciones; documentar clases Vertice, Arista, Grafo, Dijkstra, FloydWarshall, Prim, Kruskal y ConjuntosDisjuntos. 

2.  Separar modelo, algoritmos, lectura de archivos, pruebas, resultados y presentación; exponer interfaces claras y no mezclar las dos unidades de medida. 

3.  Implementar validaciones para ids inexistentes, pesos negativos en caminos mínimos, aristas duplicadas e inconsistencias en el CSV. 

### **Etapa D. Dijkstra** 

1.  Ejecutar desde N02 y N03, informar distancias y ruta reconstruida hacia N06, N10, N14, N20. 

2.  Registrar las extracciones de la cola de prioridad y las relajaciones de aristas del grafo manual de seis nodos. 

3.  Explicar heapq y analizar tiempo O((V+E) log V) con lista de adyacencia; contrastar con una implementación de matriz, si la desarrollan. 

### **Etapa E. Floyd-Warshall** 

1.  Calcular la matriz completa de distancias mínimas para los 24 vértices y mostrar una matriz next o equivalente para reconstruir recorridos. 

2.  Documentar estado inicial, iteraciones por vértice intermedio y resultado final en el caso manual de seis nodos. 

3.  Comparar distancias de Floyd-Warshall con las obtenidas por Dijkstra ejecutado desde todos los orígenes; justificar O(V³) tiempo y O(V²) memoria. 

### **Etapa F. Prim** 

1.  Construir el árbol de expansión mínima utilizando exclusivamente el peso de red; reportar aristas elegidas, 23 aristas finales y costo total. 

2.  Documentar la frontera de selección y cómo se evitan ciclos; ejecutar desde dos vértices iniciales y discutir empates. 

3.  Analizar complejidad de la variante implementada y el tipo de estructura utilizada para candidatos. 

### **Etapa G. Kruskal** 

1.  Ordenar aristas por peso de red, implementar ConjuntosDisjuntos con find y union, compresión de caminos y unión por rango/tamaño. 

2.  Registrar aristas aceptadas y descartadas del caso manual, incluidos los rechazos que crearían ciclos. 

3.  Contrastar costo total de Kruskal con Prim y distinguir costo coincidente de identidad exacta del conjunto de aristas. 

Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 3 

**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

### **Etapa H. Experimentos y conclusiones** 

1.  Ejecutar el escenario especial asignado al grupo con una copia de los datos originales y presentar un antes/después. 

2.  Generar grafos sintéticos reproducibles de 100 y 200 vértices, uno disperso y otro denso; medir únicamente el tiempo de cada algoritmo con perf_counter (excluir entrada/salida y gráficos). 

3.  Entregar pruebas automatizadas, interpretación contextual, recomendaciones, limitaciones y evidencias individuales de dominio. 

## **09  Escenario especial obligatorio** 

Eliminar simultáneamente N02–N08 y N15–N21, medir pérdida de accesibilidad y recalcular el árbol mínimo de la red remanente si es conexa. 

- Conservar la instancia base intacta y registrar exactamente qué dato o arista se modifica. 

- Ejecutar nuevamente los algoritmos afectados por el cambio y mostrar diferencias cuantitativas. 

- Justificar si el resultado es una ruta, una distancia entre pares, un árbol o un bosque. 

- Explicar por qué el nuevo resultado es técnicamente válido en el contexto del caso. 

## **10  Diseño OO obligatorio** 

|**Clase / módulo**|**Responsabilidad verificable**|
|---|---|
|Clase Vertice|id, nombre, rol, metadatos; igualdad por identificador estable.|
|Clase Arista|origen, destino, peso_ruta, peso_red; validación de no negatividad y consistencia.|
|Clase Grafo|agregar/eliminar vértice o arista, vecinos, consulta de pesos, copia de escenario, representaciones,<br>conectividad.|
|Clase Dijkstra|calcular_desde(origen) -> distancias y predecesores; reconstruir_camino(destino).|
|Clase FloydWarshall|calcular_todos() -> matriz_distancias y matriz_siguiente; reconstruir_camino(origen,destino).|
|Clase Prim|calcular_arbol(inicio) -> aristas_seleccionadas, costo_total.|
|Clase Kruskal|calcular_arbol() -> aristas_seleccionadas, costo_total.|
|Clase<br>ConjuntosDisjuntos|find, union, inicialización, compresión de caminos y unión por rango o tamaño.|
|Capa de entrada y salida|leer CSV, validar datos, mostrar tabla de resultados, exportar resultados reproducibles.|



Entrega UML. Diagrama de clases legible con atributos, métodos, visibilidad y relaciones. El código debe respetar el diagrama, o documentar explícitamente las divergencias justificadas. 

## **11  Caso pequeño: resolución manual paso a paso** 

Antes de ejecutar el sistema, resuelva manualmente un grafo independiente de 6 nodos (A, B, C, D, E, F) y 9 aristas no dirigidas. Use peso_ruta para los caminos y peso_red para expansión mínima. No se proporciona la respuesta: forma parte de la evaluación. 

|**Origen**|**Destino**|**Peso ruta**|**Peso red**|
|---|---|---|---|
|A|B|7|9|
|A|C|16|13|
|B|C|3|16|
|B|D|12|19|
|C|D|17|19|
|C|E|13|21|
|D|E|15|23|
|D|F|8|23|
|E|F|13|21|



1.  Dijkstra desde A: tabla por iteración con vértice extraído, distancias tentativas y predecesores; reconstruya el camino a F. 

2.  Floyd-Warshall: matriz inicial, dos iteraciones intermedias explicadas y matriz final; detalle la consulta A→F. 

3.  Prim desde A: registre frontera, arista elegida, vértice incorporado y costo acumulado en cada paso. 

4.  Kruskal: ordene las 9 aristas por peso_red; justifique aceptación/rechazo y funcionamiento de Union-Find. 

5.  Compare las distancias de A y los costos finales de ambos árboles; explique cualquier empate. 

Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 4 

**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

## **12  Plan de pruebas y criterios de corrección** 

|**Prueba**|**Condición esperada / evidencia**|
|---|---|
|P1 · Modelo original|24 vértices, 48 aristas únicas, pesos positivos, simetría y conectividad.|
|P2 · Dijkstra/Floyd|Las distancias coinciden para los mismos pares cuando se usa el mismo peso.|
|P3 · Reconstrucción|Toda ruta reconstruida tiene continuidad entre aristas y su suma coincide con distancia reportada.|
|P4 · Prim/Kruskal|En instancia base: 24 vértices, 23 aristas, sin ciclos, conectividad y mismo costo total óptimo.|
|P5 · No conexo|Desconectar expresamente un vértice; indicar inalcanzabilidad; MST inexistente o bosque<br>explicitado.|
|P6 · Empate de pesos|Probar aristas con igual peso: explicar que pueden cambiar las aristas del MST, no el costo óptimo.|
|P7 · Entradas<br>erróneas|Validar identificadores inexistentes, CSV defectuoso, valores faltantes y pesos negativos.|
|P8 · Escalabilidad|Medir con grafos de 24, 100 y 200 vértices; documentar densidad E/V y repetición de pruebas.|
|P9 · Escenario<br>especial|Tabla antes/después, caminos y costo total afectados, e interpretación de cambios.|



Rendimiento. Usar time.perf_counter y al menos cinco repeticiones por configuración; reportar mediana y entorno de ejecución. Crear grafos de prueba reproducibles con semilla fija, sin incluir el costo de leer archivos o dibujar gráficos en el cronometraje. 

## **13  Análisis de complejidad exigido** 

|**Algoritmo**|**Análisis que debe sustentar**|
|---|---|
|Dijkstra|Con heap y lista: O((V+E) log V), con la salvedad de variantes y representación; espacio<br>O(V+E).|
|Floyd-Warshall|O(V³) tiempo y O(V²) espacio para matrices.|
|Prim|Explicar O(E log V) con heap + lista de adyacencia y su memoria; distinguir otras variantes.|
|Kruskal|O(E log E) por ordenamiento, Union-Find casi constante amortizado; discutir memoria.|



Se debe contrastar la complejidad teórica con tiempos empíricos, sin concluir superioridad universal desde una única ejecución o hardware. 

## **14  Preguntas de interpretación obligatorias** 

1.  ¿Qué albergues quedan más alejados, en tiempo mínimo, del Almacén Norte? 

2.  ¿Cuánto aumenta la mejor ruta al quedar inhabilitados dos corredores? 

3.  ¿Qué pares de instalaciones quedan inaccesibles, si los hay? 

4.  ¿Cuál es la red de radio de despliegue más económico antes del desastre? 

5.  ¿Qué puntos quedarían vulnerables si se pierde una arista del MST? 

6.  ¿Qué diferencia matemática y operativa existe entre un camino mínimo y un árbol de expansión mínima? 

7.  ¿Cómo cambian la solución y la complejidad con otra representación del grafo? 

8.  ¿Qué decisión no puede sostenerse exclusivamente con el modelo? La simulación no representa demanda, prioridad humanitaria, capacidad de caminos ni incertidumbre del desastre. 

## **15  Reto de ampliación (nivel sobresaliente)** 

Agregar una segunda conexión estratégica y sustentar su costo-beneficio mediante el número de nodos que permanecen conectados ante una falla. 

El reto debe mantener el núcleo del trabajo correctamente resuelto; especificar objetivos, datos adicionales, modificaciones de clases y evidencia verificable. No se permite sustituir uno de los cuatro algoritmos obligatorios. 

## **16  Entregables y organización del proyecto** 

|**Producto**|**Contenido mínimo**|
|---|---|
|Informe técnico|Problema, objetivos, supuestos, modelo, UML, decisiones de estructuras, trazas, algoritmos, resultados, validación,|
|(.docx/.pdf)|complejidad, pruebas, análisis crítico, referencias.|
|Código Python (.py)|Clases separadas por responsabilidad, comentarios útiles, instrucciones y ejecución reproducible.|
|Datos (.csv)|CSV originales y de escenarios; generadores y semilla de experimentos.|
|Pruebas|Pruebas automáticas, salidas de consola y evidencia de corrección.<br>i|
|Visualizaciones|Grafo inicial, caminos seleccionados, árboles obtenidos y al menos una figura antes/después.|
|Diapositivas|Presentación breve con foco en la interpretación, comparaciones y decisiones de implementación.<br>i|
|Demostración|Ejecución en vivo, entrada modificada, resultado y sustentación individual.|



Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 5 

**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

Estructura sugerida: src/modelo, src/algoritmos, src/io, tests, datos, resultados, informe, presentacion, README.md. Es una sugerencia, no un requisito de nombres. 

## **17  Rúbrica de evaluación (20 puntos)** 

|**Criterio**|**Punto**<br>**s**|**Evidencia de nivel excelente**|
|---|---|---|
|Análisis y modelado del caso|3|Modelo semánticamente correcto; supuestos, unidades, grafo y justificación claros.|
|Diseño OO y UML|3|Responsabilidades cohesivas, interfaz limpia, modularidad, validación y diagrama<br>consistente.|
|Dijkstra|2|Implementación propia correcta, estructura adecuada, rutas reconstruidas y evidencia<br>manual.|
|Floyd-Warshall|2|Matriz de distancias y reconstrucción correctas; validación cruzada.|
|Prim|2|Árbol mínimo correcto con 23 aristas y costo bien calculado en el grafo original.|
|Kruskal y Union-Find|2|Ordenación, detección de ciclos, conjuntos disjuntos y costo correctos.|
|Pruebas, complejidad y comparación|3|Casos límite, escalabilidad, métricas reproducibles y conclusiones de rendimiento.|
|Interpretación y sustentación individual|3|Respuestas técnicas, demo funcional, lectura crítica de resultados y límites del modelo.|



Niveles de logro por criterio: excelente = 100 % del puntaje; satisfactorio = 75 %; básico = 50 %; insuficiente = 0–25 %, de acuerdo con la evidencia. Puntaje total: 20 puntos. 

### **Descriptores de desempeño observables** 

**Análisis y modelado.** Excelente: ambos objetivos, unidades, propiedades e hipótesis correctos.  Satisfactorio: modelo correcto con una justificación parcial.  Básico: omite restricciones o confunde una relación.  Insuficiente: modelo inválido o no justificable. 

**Diseño OO y UML.** Excelente: clases cohesionadas, interfaces, pruebas y UML coherentes.  Satisfactorio: arquitectura adecuada con detalles menores.  Básico: acoplamiento elevado y UML incompleto.  Insuficiente: no utiliza un diseño OO defendible. 

**Dijkstra.** Excelente: distancias y rutas correctas, traza y heap explicados.  Satisfactorio: funciona con omisiones menores de evidencia.  Básico: errores de reconstrucción o casos límite.  Insuficiente: rutas incorrectas o algoritmo no implementado. **Floyd-Warshall.** Excelente: matrices, caminos y comparación cruzada exactos.  Satisfactorio: matrices correctas con explicación parcial.  Básico: cálculo parcial o matriz de caminos defectuosa.  Insuficiente: distancias no confiables o inexistentes. 

**Prim.** Excelente: árbol válido, óptimo y razonamiento paso a paso.  Satisfactorio: árbol correcto con evidencia incompleta. Básico: no explica selección o falla en empates.  Insuficiente: contiene ciclos o no abarca los nodos. 

**Kruskal.** Excelente: ordenamiento y Union-Find correctos; árbol óptimo.  Satisfactorio: resultado correcto con justificación parcial.  Básico: Union-Find débil o trazas incompletas.  Insuficiente: ciclos no controlados o costo erróneo. 

**Pruebas y rendimiento.** Excelente: invariantes, límites y tiempos reproducibles interpretados.  Satisfactorio: cobertura suficiente con comparación básica.  Básico: pocas pruebas o tiempos poco controlados.  Insuficiente: carece de evidencias de validación. 

**Sustentación.** Excelente: todos explican código, decisiones y limitaciones.  Satisfactorio: dominio general con dudas puntuales. Básico: respuestas parciales o dependencia de la demostración.  Insuficiente: no explica funcionamiento o resultados. 

## **18  Sustentación y preguntas individuales** 

1.  ¿Qué significa infinito en una matriz de Floyd-Warshall? 

2.  ¿Qué produce Kruskal si la red se divide en componentes? 

3.  ¿Por qué el MST puede ser insuficiente en emergencias? 

4.  ¿Cómo reconstruye un camino alternativo? 

5.  ¿Qué indicadores permitirían priorizar un albergue vulnerable? 

6.  Explique cuándo conviene ejecutar Dijkstra múltiples veces y cuándo una matriz completa de Floyd-Warshall. 

7.  Demuestre cómo evita ciclos al seleccionar una arista en Kruskal. 

8.  Justifique cómo verificó que el árbol mínimo cubre todos los vértices y contiene V−1 aristas. 

9.  ¿Por qué no es válido usar aristas de peso negativo en la implementación estándar de Dijkstra? 

10.  Muestre en el código dónde se reconstruyen los caminos y cómo se controlan las rutas inexistentes. 

Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 6 

**ESTRUCTURA DE DATOS ORIENTADA A OBJETOS   |   ALGORITMOS DE GRAFOS** 

## **19  Condiciones de evaluación y buenas prácticas** 

- Todo integrante debe poder explicar el modelo, el código y las salidas; el docente podrá solicitar una variación de pesos o enlaces en vivo. 

- No se aceptan soluciones basadas únicamente en una llamada a bibliotecas que ya implementan los algoritmos. 

- Los gráficos son apoyo: la prueba de corrección debe apoyarse en distancias, predecesores, costos, invariantes y casos límite. 

- Las mediciones sintéticas no deben presentarse como datos reales del municipio, hospital, empresa o universidad. 

- Documentar fuentes académicas y técnicas efectivamente consultadas; citar conforme a APA 7. 

## **20  Lista de comprobación previa a la entrega** 

**Código y modelo.** CSV importables y validados; cuatro algoritmos propios documentados; matriz y lista de adyacencia; UML coherente; rutas reconstruidas con sus pesos. 

**Resultados y evidencias.** Mismo costo óptimo de Prim y Kruskal en la instancia base; traza manual, pruebas, experimento especial, análisis de complejidad, sustentación y archivos editables reproducibles. 

Guía académica · Dijkstra · Floyd-Warshall · Prim · Kruskal  |  Página 7 

