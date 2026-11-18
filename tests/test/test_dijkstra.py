import unittest
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from datos import cargar_grafo_base, cargar_grafo_manual
from dijkstra import Dijkstra

class TestDijkstra(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba para preparar los datos."""
        self.grafo_base = cargar_grafo_base("../datos")
        self.grafo_manual = cargar_grafo_manual("../datos/grafo_manual.csv")
        
    def test_caso_manual_AF(self):
        """Evalúa resolver manualmente desde A y reconstruir A-F."""
        dij = Dijkstra(self.grafo_manual)
        distancias, predecesores = dij.calcular_desde("A")
        
        self.assertEqual(distancias["A"], 0)
        self.assertNotEqual(distancias["F"], math.inf)
        
        ruta_f = dij.reconstruir_camino("F")
        self.assertIsNotNone(ruta_f)
        self.assertEqual(ruta_f[0], "A")
        self.assertEqual(ruta_f[-1], "F")

    def test_ocho_rutas_completas(self):
        """Ejecutar desde N02 y N03 hacia N06, N10, N14 y N20."""
        dij = Dijkstra(self.grafo_base)
        destinos = ["N06", "N10", "N14", "N20"]
        
        for origen in ["N02", "N03"]:
            distancias, _ = dij.calcular_desde(origen)
            
            for destino in destinos:
                ruta = dij.reconstruir_camino(destino)
                self.assertIsNotNone(ruta)
                self.assertEqual(ruta[0], origen)
                self.assertEqual(ruta[-1], destino)
                self.assertTrue(distancias[destino] > 0)

    def test_albergues_mas_alejados_desde_N02(self):
        """Compara los tiempos a los albergues N06-N10 y señala los más alejados."""
        dij = Dijkstra(self.grafo_base)
        distancias, _ = dij.calcular_desde("N02")
        
        albergues = ["N06", "N07", "N08", "N09", "N10"]
        tiempos = {nodo: distancias[nodo] for nodo in albergues}
        
        tiempo_max = max(tiempos.values())
        mas_alejados = [nodo for nodo, t in tiempos.items() if t == tiempo_max]
 
        self.assertTrue(len(mas_alejados) >= 1)

        print(f"\n[DATO PARA INFORME] Nodos más alejados de N02 (Rango N06-N10): {mas_alejados} con {tiempo_max} min.")

if __name__ == "__main__":
    unittest.main()