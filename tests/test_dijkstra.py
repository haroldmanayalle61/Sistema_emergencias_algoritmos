import unittest
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datos import cargar_grafo_base, cargar_grafo_manual
from dijkstra import Dijkstra
from modelo import Vertice

DATOS = RAIZ / "datos"

class TestDijkstra(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba para preparar los datos."""
        self.grafo_base = cargar_grafo_base(DATOS)
        self.grafo_manual = cargar_grafo_manual(DATOS / "grafo_manual.csv")
        
    def test_caso_manual_AF(self):
        """Evalúa resolver manualmente desde A y reconstruir A-F."""
        dij = Dijkstra(self.grafo_manual)
        distancias, predecesores = dij.calcular_desde("A")
        
        self.assertEqual(distancias, {"A": 0, "B": 7, "C": 10, "D": 19, "E": 23, "F": 27})
        self.assertEqual(predecesores["F"], "D")
        
        ruta_f = dij.reconstruir_camino("F")
        self.assertEqual(ruta_f, ["A", "B", "D", "F"])

    def test_ocho_rutas_completas(self):
        """Ejecutar desde N02 y N03 hacia N06, N10, N14 y N20."""
        dij = Dijkstra(self.grafo_base)
        destinos = ["N06", "N10", "N14", "N20"]
        esperadas = {"N02": [96, 57, 48, 69], "N03": [74, 35, 50, 71]}
        
        for origen in ["N02", "N03"]:
            distancias, _ = dij.calcular_desde(origen)
            
            for destino, esperada in zip(destinos, esperadas[origen]):
                with self.subTest(origen=origen, destino=destino):
                    ruta = dij.reconstruir_camino(destino)
                    self.assertIsNotNone(ruta)
                    self.assertEqual(ruta[0], origen)
                    self.assertEqual(ruta[-1], destino)
                    self.assertEqual(distancias[destino], esperada)
                    total = 0
                    for a, b in zip(ruta, ruta[1:]):
                        self.assertTrue(self.grafo_base.tiene_arista(a, b))
                        total += self.grafo_base.peso(a, b, "peso_ruta")
                    self.assertEqual(total, distancias[destino])

    def test_albergues_mas_alejados_desde_N02(self):
        """Compara los tiempos a los albergues N06-N10 y señala los más alejados."""
        dij = Dijkstra(self.grafo_base)
        distancias, _ = dij.calcular_desde("N02")
        
        albergues = ["N06", "N07", "N08", "N09", "N10"]
        tiempos = {nodo: distancias[nodo] for nodo in albergues}
        
        tiempo_max = max(tiempos.values())
        mas_alejados = [nodo for nodo, t in tiempos.items() if t == tiempo_max]
 
        self.assertEqual(mas_alejados, ["N06"])
        self.assertEqual(tiempo_max, 96)

        print(f"\n[DATO PARA INFORME] Nodos más alejados de N02 (Rango N06-N10): {mas_alejados} con {tiempo_max} min.")

    def test_recalcular_elimina_vertices_antiguos_y_conserva_resultados_previos(self):
        dij = Dijkstra(self.grafo_manual)
        distancias_antes, predecesores_antes = dij.calcular_desde("A")
        copia_distancias = dict(distancias_antes)
        copia_predecesores = dict(predecesores_antes)

        self.grafo_manual.eliminar_vertice("F")
        distancias, predecesores = dij.calcular_desde("B")

        self.assertEqual(set(distancias), set("ABCDE"))
        self.assertEqual(set(predecesores), set("ABCDE"))
        self.assertEqual(distancias["B"], 0)
        self.assertIsNone(predecesores["B"])
        self.assertEqual(dij.reconstruir_camino("A"), ["B", "A"])
        self.assertIsNot(distancias, distancias_antes)
        self.assertIsNot(predecesores, predecesores_antes)
        self.assertEqual(distancias_antes, copia_distancias)
        self.assertEqual(predecesores_antes, copia_predecesores)

    def test_destino_inalcanzable(self):
        self.grafo_manual.agregar_vertice(Vertice("Z"))
        dij = Dijkstra(self.grafo_manual)
        distancias, predecesores = dij.calcular_desde("A")
        self.assertEqual(distancias["Z"], math.inf)
        self.assertIsNone(predecesores["Z"])
        self.assertIsNone(dij.reconstruir_camino("Z"))

    def test_origen_igual_a_destino(self):
        dij = Dijkstra(self.grafo_manual)
        distancias, _ = dij.calcular_desde("A")
        self.assertEqual(distancias["A"], 0)
        self.assertEqual(dij.reconstruir_camino("A"), ["A"])

    def test_identificadores_inexistentes(self):
        dij = Dijkstra(self.grafo_manual)
        with self.assertRaises(KeyError):
            dij.calcular_desde("Z")
        dij.calcular_desde("A")
        with self.assertRaises(KeyError):
            dij.reconstruir_camino("Z")

    def test_reconstruir_sin_calculo_previo(self):
        dij = Dijkstra(self.grafo_manual)
        with self.assertRaises(ValueError):
            dij.reconstruir_camino("F")

    def test_traza_registra_extracciones_mejoras_y_entradas_antiguas(self):
        dij = Dijkstra(self.grafo_manual, registrar_traza=True)
        distancias, _ = dij.calcular_desde("A")
        extracciones = [p for p in dij.traza if p["evento"] == "extraccion"]
        self.assertEqual(extracciones[0]["vertice"], "A")
        self.assertEqual(extracciones[0]["distancias"]["C"], math.inf)
        self.assertIsNone(extracciones[0]["predecesores"]["C"])
        self.assertEqual(distancias["C"], 10)
        self.assertTrue(any(
            p["vertice"] == "C" and p["distancia"] == 16 and p["descartada"]
            for p in extracciones
        ))
        self.assertIn({
            "evento": "relajacion", "origen": "B", "destino": "C",
            "distancia_anterior": 16, "distancia_nueva": 10,
        }, dij.traza)

        traza_anterior = dij.traza
        dij.calcular_desde("A")
        self.assertIsNot(dij.traza, traza_anterior)
        self.assertEqual(dij.traza, traza_anterior)

    def test_traza_opcional_conserva_resultados(self):
        sin_traza = Dijkstra(self.grafo_manual)
        con_traza = Dijkstra(self.grafo_manual, registrar_traza=True)
        self.assertEqual(sin_traza.calcular_desde("A"), con_traza.calcular_desde("A"))
        self.assertEqual(sin_traza.traza, [])
        self.assertTrue(con_traza.traza)

if __name__ == "__main__":
    unittest.main(verbosity=2)
