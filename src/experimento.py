"""Experimentos de rendimiento de los algoritmos."""

import csv
import platform
from pathlib import Path
from statistics import median
from time import perf_counter

from datos import cargar_grafo_base, generar_configuracion
from dijkstra import Dijkstra
from floyd_warshall import FloydWarshall
from prim import Prim
from kruskal import Kruskal


# Carpeta principal del proyecto.
RAIZ = Path(__file__).resolve().parents[1]

REPETICIONES = 5
SEMILLA = 2026


def medir(grafo, nombre):
    """Ejecuta un algoritmo cinco veces y devuelve sus tiempos."""
    tiempos = []
    ids = grafo.ids()
    origen = ids[0]

    for _ in range(REPETICIONES):
        # Preparar los objetos fuera del tiempo medido.
        # Sus trazas están desactivadas por defecto.
        dijkstra = Dijkstra(grafo)
        floyd = FloydWarshall(grafo)
        prim = Prim(grafo)
        kruskal = Kruskal(grafo)

        inicio = perf_counter()

        if nombre == "Dijkstra una fuente":
            dijkstra.calcular_desde(origen)

        elif nombre == "Dijkstra todos":
            for vertice in ids:
                dijkstra.calcular_desde(vertice)

        elif nombre == "Floyd-Warshall":
            floyd.calcular_todos()

        elif nombre == "Prim":
            prim.calcular_arbol(origen)

        elif nombre == "Kruskal":
            kruskal.calcular_arbol()

        else:
            raise ValueError("Algoritmo desconocido")

        fin = perf_counter()

        # Convertir segundos a milisegundos.
        tiempo = (fin - inicio) * 1000
        tiempos.append(tiempo)

    return tiempos


def ejecutar_experimentos():  # sourcery skip: extract-method, for-append-to-extend
    """Prepara los grafos, mide los algoritmos y guarda los resultados."""

    # 1. Cargar y generar los grafos antes de medir.
    escenarios = {
        "24_base": cargar_grafo_base(RAIZ / "datos"),
    }

    configuraciones = [
        "100_disperso",
        "100_denso",
        "200_disperso",
        "200_denso",
    ]

    for nombre in configuraciones:
        escenarios[nombre] = generar_configuracion(
            nombre, semilla=SEMILLA
        )

    algoritmos = [
        "Dijkstra una fuente",
        "Dijkstra todos",
        "Floyd-Warshall",
        "Prim",
        "Kruskal",
    ]

    # 2. Ejecutar las mediciones.
    resultados = []

    for nombre_escenario, grafo in escenarios.items():
        vertices = grafo.num_vertices
        aristas = grafo.num_aristas

        print(f"\nEscenario: {nombre_escenario}")
        print(f"Vertices: {vertices} | Aristas: {aristas}")

        for algoritmo in algoritmos:
            tiempos = medir(grafo, algoritmo)
            tiempo_mediano = median(tiempos)

            print(f"{algoritmo}: {tiempo_mediano:.6f} ms")

            # Una fila por algoritmo y escenario.
            fila = [
                nombre_escenario,
                vertices,
                aristas,
                aristas / vertices,
                algoritmo,
                REPETICIONES,
                tiempo_mediano,
            ]

            # Agregar los cinco tiempos como evidencia.
            fila.extend(tiempos)
            resultados.append(fila)

    # 3. Guardar la tabla después de terminar las mediciones.
    carpeta = RAIZ / "resultados"
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta_csv = carpeta / "rendimiento.csv"

    encabezados = [
        "escenario",
        "vertices",
        "aristas",
        "E_sobre_V",
        "algoritmo",
        "repeticiones",
        "mediana_ms",
    ]

    for numero in range(1, REPETICIONES + 1):
        encabezados.append(f"tiempo_{numero}_ms")

    with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)
        escritor.writerows(resultados)

    # 4. Guardar las condiciones del experimento.
    ruta_entorno = carpeta / "entorno_experimento.txt"

    with open(ruta_entorno, "w", encoding="utf-8") as archivo:
        archivo.write(f"Python: {platform.python_version()}\n")
        archivo.write(f"Sistema: {platform.platform()}\n")
        archivo.write(f"Procesador: {platform.processor()}\n")
        archivo.write(f"Semilla de grafos sinteticos: {SEMILLA}\n")
        archivo.write(f"Repeticiones: {REPETICIONES}\n")
        archivo.write("Unidad de los tiempos: milisegundos\n")
        archivo.write("Origen de Dijkstra y Prim: primer id del grafo\n")
        archivo.write(
            "Se mide el calculo, incluida su inicializacion interna.\n"
        )
        archivo.write(
            "Se excluyen carga, generacion de grafos, constructores, "
            "dibujos, impresiones y guardado de archivos.\n"
        )
        archivo.write("Las trazas estan desactivadas.\n")
        archivo.write(
            "Dijkstra todos calcula desde cada origen, pero solo "
            "conserva el resultado del ultimo origen.\n"
        )
        archivo.write(
            "Floyd-Warshall conserva las matrices de todos los pares.\n"
        )

    print(f"\nTabla guardada en: {ruta_csv}")
    print(f"Entorno guardado en: {ruta_entorno}")


if __name__ == "__main__":
    ejecutar_experimentos()