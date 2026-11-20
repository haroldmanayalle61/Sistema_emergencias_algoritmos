"""Pruebas del algoritmo Floyd-Warshall."""

import math
import sys
import unittest
from pathlib import Path

# Permite importar los módulos de la carpeta src.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datos import cargar_grafo_base, cargar_grafo_manual
from dijkstra import Dijkstra
from floyd_warshall import FloydWarshall
from modelo import Arista, Grafo, PESO_RUTA, Vertice


class TestFloydWarshall(unittest.TestCase):

    def setUp(self):
        """Cada prueba recibe grafos nuevos e independientes."""
        self.grafo = cargar_grafo_base(RAIZ / "datos")
        self.manual = cargar_grafo_manual(
            RAIZ / "datos" / "grafo_manual.csv"
        )

    def comprobar_camino(self, grafo, camino, origen, destino, distancia):
        """Verifica extremos, conexiones y tiempo total de una ruta."""
        self.assertIsNotNone(camino)
        self.assertEqual(camino[0], origen)
        self.assertEqual(camino[-1], destino)

        tiempo_total = 0

        for posicion in range(len(camino) - 1):
            actual = camino[posicion]
            siguiente = camino[posicion + 1]

            arista = grafo.obtener_arista(actual, siguiente)
            self.assertIsNotNone(arista)

            tiempo_total += arista.peso(PESO_RUTA)

        self.assertAlmostEqual(tiempo_total, distancia)

    def test_matriz_final_caso_manual(self):
        """Comprueba todos los resultados del grafo manual."""
        floyd = FloydWarshall(self.manual)
        distancias, siguiente = floyd.calcular_todos()

        ids_esperados = ["A", "B", "C", "D", "E", "F"]

        matriz_esperada = [
            [0, 7, 10, 19, 23, 27],
            [7, 0, 3, 12, 16, 20],
            [10, 3, 0, 15, 13, 23],
            [19, 12, 15, 0, 15, 8],
            [23, 16, 13, 15, 0, 13],
            [27, 20, 23, 8, 13, 0],
        ]

        # Consultamos por id para no depender del orden de la matriz.
        for i, origen in enumerate(ids_esperados):
            for j, destino in enumerate(ids_esperados):
                with self.subTest(origen=origen, destino=destino):
                    fila = floyd.indice[origen]
                    columna = floyd.indice[destino]

                    self.assertEqual(
                        distancias[fila][columna],
                        matriz_esperada[i][j],
                    )

        self.assertEqual(len(siguiente), 6)

    def test_camino_manual_de_a_hasta_f(self):
        floyd = FloydWarshall(self.manual)
        distancias, _ = floyd.calcular_todos()

        camino = floyd.reconstruir_camino("A", "F")

        self.assertEqual(camino, ["A", "B", "D", "F"])

        i = floyd.indice["A"]
        j = floyd.indice["F"]

        self.assertEqual(distancias[i][j], 27)

        self.comprobar_camino(
            self.manual, camino, "A", "F", distancias[i][j]
        )

    def test_coincide_con_dijkstra_desde_todos_los_origenes(self):
        """Compara las distancias de los 24 orígenes y sus destinos."""
        floyd = FloydWarshall(self.grafo)
        distancias_floyd, _ = floyd.calcular_todos()

        dijkstra = Dijkstra(self.grafo)

        for origen in self.grafo.ids():
            distancias_dijkstra, _ = dijkstra.calcular_desde(origen)

            for destino in self.grafo.ids():
                with self.subTest(origen=origen, destino=destino):
                    i = floyd.indice[origen]
                    j = floyd.indice[destino]

                    self.assertAlmostEqual(
                        distancias_floyd[i][j],
                        distancias_dijkstra[destino],
                    )

    def test_rutas_del_grafo_base_son_validas(self):
        """Comprueba todas las rutas reconstruidas del grafo base."""
        floyd = FloydWarshall(self.grafo)
        distancias, _ = floyd.calcular_todos()

        for origen in self.grafo.ids():
            for destino in self.grafo.ids():
                with self.subTest(origen=origen, destino=destino):
                    camino = floyd.reconstruir_camino(origen, destino)

                    i = floyd.indice[origen]
                    j = floyd.indice[destino]

                    self.comprobar_camino(
                        self.grafo,
                        camino,
                        origen,
                        destino,
                        distancias[i][j],
                    )

    def test_origen_igual_a_destino(self):
        floyd = FloydWarshall(self.grafo)
        distancias, _ = floyd.calcular_todos()

        for id_vertice in self.grafo.ids():
            with self.subTest(vertice=id_vertice):
                posicion = floyd.indice[id_vertice]

                self.assertEqual(distancias[posicion][posicion], 0)
                self.assertEqual(
                    floyd.reconstruir_camino(id_vertice, id_vertice),
                    [id_vertice],
                )

    def test_destino_inalcanzable(self):
        """Un vértice aislado debe tener distancia infinita."""
        self.manual.agregar_vertice(Vertice("Z"))

        floyd = FloydWarshall(self.manual)
        distancias, siguiente = floyd.calcular_todos()

        i = floyd.indice["A"]
        j = floyd.indice["Z"]

        self.assertEqual(distancias[i][j], math.inf)
        self.assertEqual(distancias[j][i], math.inf)
        self.assertIsNone(siguiente[i][j])

        self.assertIsNone(floyd.reconstruir_camino("A", "Z"))
        self.assertIsNone(floyd.reconstruir_camino("Z", "A"))

        # El vértice aislado sí puede consultarse consigo mismo.
        self.assertEqual(floyd.reconstruir_camino("Z", "Z"), ["Z"])

    def test_identificadores_inexistentes(self):
        floyd = FloydWarshall(self.grafo)
        floyd.calcular_todos()

        with self.assertRaises(KeyError):
            floyd.reconstruir_camino("NO_EXISTE", "N02")

        with self.assertRaises(KeyError):
            floyd.reconstruir_camino("N02", "NO_EXISTE")

    def test_tipos_incorrectos_en_consulta(self):
        floyd = FloydWarshall(self.grafo)
        floyd.calcular_todos()

        with self.assertRaises(TypeError):
            floyd.reconstruir_camino(2, "N03")

        with self.assertRaises(TypeError):
            floyd.reconstruir_camino("N02", None)

    def test_reconstruir_sin_calculo_previo(self):
        floyd = FloydWarshall(self.grafo)

        with self.assertRaises(ValueError):
            floyd.reconstruir_camino("N02", "N06")

    def test_constructor_invalido(self):
        with self.assertRaises(TypeError):
            FloydWarshall(None)

        with self.assertRaises(TypeError):
            FloydWarshall(self.grafo, registrar_traza="si")

    def test_recalculo_actualiza_rutas(self):
        """El algoritmo debe considerar los cambios en el grafo."""
        floyd = FloydWarshall(self.manual)

        distancias_anteriores, _ = floyd.calcular_todos()
        i = floyd.indice["A"]
        j = floyd.indice["F"]

        self.assertEqual(distancias_anteriores[i][j], 27)

        # Una conexión nueva mejora la ruta de A a F.
        self.manual.agregar_arista(Arista("A", "F", 2, 50))

        distancias_nuevas, _ = floyd.calcular_todos()

        self.assertEqual(distancias_nuevas[i][j], 2)
        self.assertEqual(
            floyd.reconstruir_camino("A", "F"),
            ["A", "F"],
        )

        # El resultado anterior debe conservar sus valores.
        self.assertEqual(distancias_anteriores[i][j], 27)

    def test_recalculo_elimina_ids_antiguos(self):
        floyd = FloydWarshall(self.manual)
        floyd.calcular_todos()

        self.manual.eliminar_vertice("F")
        floyd.calcular_todos()

        self.assertNotIn("F", floyd.ids)
        self.assertNotIn("F", floyd.indice)
        self.assertEqual(len(floyd.matriz_distancias), 5)

        with self.assertRaises(KeyError):
            floyd.reconstruir_camino("A", "F")

    def test_traza_guarda_inicio_y_cada_intermedio(self):
        floyd = FloydWarshall(self.manual, registrar_traza=True)
        distancias, _ = floyd.calcular_todos()

        # Un estado inicial y seis estados por los intermediarios.
        self.assertEqual(len(floyd.traza), 7)
        self.assertIsNone(floyd.traza[0]["intermedio"])

        intermediarios = [
            paso["intermedio"] for paso in floyd.traza[1:]
        ]
        self.assertEqual(intermediarios, floyd.ids)

        i = floyd.indice["A"]
        j = floyd.indice["C"]

        # Al inicio A-C cuesta 16; pasando por B baja a 10.
        self.assertEqual(
            floyd.traza[0]["matriz_distancias"][i][j], 16
        )

        paso_b = next(
            paso for paso in floyd.traza
            if paso["intermedio"] == "B"
        )

        self.assertEqual(paso_b["matriz_distancias"][i][j], 10)
        self.assertEqual(
            floyd.traza[-1]["matriz_distancias"],
            distancias,
        )

        # Las copias de la traza no deben cambiar con el resultado.
        distancias[i][j] = 999
        self.assertEqual(paso_b["matriz_distancias"][i][j], 10)

        # Al recalcular, la traza se reinicia.
        floyd.calcular_todos()
        self.assertEqual(len(floyd.traza), 7)

    def test_traza_opcional_conserva_resultados(self):
        sin_traza = FloydWarshall(self.manual)
        con_traza = FloydWarshall(
            self.manual, registrar_traza=True
        )

        resultado_sin = sin_traza.calcular_todos()
        resultado_con = con_traza.calcular_todos()

        self.assertEqual(resultado_sin, resultado_con)
        self.assertEqual(sin_traza.traza, [])

    def test_empate_de_rutas(self):
        """Acepta cualquiera de dos caminos con el mismo tiempo."""
        grafo = Grafo()

        for id_vertice in ["A", "B", "C", "D"]:
            grafo.agregar_vertice(Vertice(id_vertice))

        grafo.agregar_arista(Arista("A", "B", 2, 10))
        grafo.agregar_arista(Arista("B", "D", 3, 10))
        grafo.agregar_arista(Arista("A", "C", 1, 10))
        grafo.agregar_arista(Arista("C", "D", 4, 10))

        floyd = FloydWarshall(grafo)
        distancias, _ = floyd.calcular_todos()
        camino = floyd.reconstruir_camino("A", "D")

        i = floyd.indice["A"]
        j = floyd.indice["D"]

        self.assertEqual(distancias[i][j], 5)
        self.assertIn(
            camino,
            [["A", "B", "D"], ["A", "C", "D"]],
        )

        self.comprobar_camino(grafo, camino, "A", "D", 5)

    def test_usa_peso_ruta_y_no_peso_red(self):
        """Los caminos deben minimizar minutos, no costo de red."""
        grafo = Grafo()

        for id_vertice in ["A", "B", "C"]:
            grafo.agregar_vertice(Vertice(id_vertice))

        grafo.agregar_arista(Arista("A", "B", 2, 100))
        grafo.agregar_arista(Arista("B", "C", 3, 100))
        grafo.agregar_arista(Arista("A", "C", 9, 1))

        floyd = FloydWarshall(grafo)
        distancias, _ = floyd.calcular_todos()

        i = floyd.indice["A"]
        j = floyd.indice["C"]

        self.assertEqual(distancias[i][j], 5)
        self.assertEqual(
            floyd.reconstruir_camino("A", "C"),
            ["A", "B", "C"],
        )

    def test_grafo_vacio(self):
        floyd = FloydWarshall(Grafo())
        distancias, siguiente = floyd.calcular_todos()

        self.assertEqual(distancias, [])
        self.assertEqual(siguiente, [])
        self.assertEqual(floyd.ids, [])

    def test_grafo_con_un_vertice(self):
        grafo = Grafo()
        grafo.agregar_vertice(Vertice("A"))

        floyd = FloydWarshall(grafo)
        distancias, siguiente = floyd.calcular_todos()

        self.assertEqual(distancias, [[0]])
        self.assertEqual(siguiente, [["A"]])
        self.assertEqual(
            floyd.reconstruir_camino("A", "A"),
            ["A"],
        )


if __name__ == "__main__":
    unittest.main()