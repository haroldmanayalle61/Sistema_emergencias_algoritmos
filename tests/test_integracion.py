"""Pruebas de integración del Sistema de Emergencias · Grupo 07."""
import csv
import io
import math
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datos import cargar_grafo
from modelo import Grafo, PESO_RUTA, PESO_RED
from sistema_emergencias import SistemaEmergencias, CIERRES_DESASTRE
from main import main


class TestIntegracion(unittest.TestCase):
    def setUp(self):
        self.s = SistemaEmergencias()
        self.base = self.s.grafo_base

    def firma(self, grafo):
        return sorted((a.clave, a.peso_ruta, a.peso_red) for a in grafo.aristas())

    def comprobar_ruta(self, grafo, camino, tiempo, origen, destino):
        if tiempo == math.inf:
            self.assertIsNone(camino)
            return
        self.assertIsNotNone(camino)
        self.assertEqual((camino[0], camino[-1]), (origen, destino))
        total = 0
        for a, b in zip(camino, camino[1:]):
            self.assertTrue(grafo.tiene_arista(a, b))
            total += grafo.peso(a, b, PESO_RUTA)
        self.assertAlmostEqual(total, tiempo)

    def comprobar_bosque(self, grafo, resultado):
        bosque = Grafo()
        for v in grafo.vertices():
            bosque.agregar_vertice(v.copiar())
        componentes = len(grafo.componentes_conexas())
        self.assertEqual(len(resultado["aristas"]), grafo.num_vertices - componentes)
        self.assertEqual(resultado["cobertura"], grafo.num_vertices)
        self.assertEqual(resultado["bosque"], componentes > 1)
        self.assertAlmostEqual(resultado["costo"], sum(a.peso_red for a in resultado["aristas"]))
        for a in resultado["aristas"]:
            self.assertTrue(grafo.tiene_arista(a.origen, a.destino))
            bosque.agregar_arista(a.copiar())
        self.assertEqual({frozenset(c) for c in bosque.componentes_conexas()},
                         {frozenset(c) for c in grafo.componentes_conexas()})

    def test_p1_modelo_base(self):
        self.assertEqual(self.s.resumen_base(), {"vertices": 24, "aristas": 48,
                         "componentes": 1, "conexo": True})
        for metrica in (PESO_RUTA, PESO_RED):
            matriz, ids = self.base.a_matriz_adyacencia(metrica)
            self.assertEqual(len(ids), 24)
            for i in range(24):
                self.assertEqual(matriz[i][i], 0)
                for j in range(24):
                    self.assertEqual(matriz[i][j], matriz[j][i])
        self.assertEqual(len({a.clave for a in self.base.aristas()}), 48)
        self.assertTrue(all(math.isfinite(p) and p > 0 for a in self.base.aristas()
                            for p in (a.peso_ruta, a.peso_red)))

    def test_p2_p3_rutas_y_distancias(self):
        for grafo in (self.base, self.s.aplicar_cierres()):
            for (o, d), (camino, tiempo) in self.s.rutas_requeridas(grafo).items():
                self.comprobar_ruta(grafo, camino, tiempo, o, d)
                camino_f, tiempo_f = self.s.camino_floyd(o, d, grafo)
                self.assertEqual(tiempo, tiempo_f)
                self.comprobar_ruta(grafo, camino_f, tiempo_f, o, d)
            matriz, _, ids = self.s.matriz_floyd(grafo)
            from dijkstra import Dijkstra
            for i, origen in enumerate(ids):
                dij = Dijkstra(grafo)
                distancias, _ = dij.calcular_desde(origen)
                for j, destino in enumerate(ids):
                    self.assertEqual(distancias[destino], matriz[i][j])
                    self.comprobar_ruta(grafo, dij.reconstruir_camino(destino),
                                        distancias[destino], origen, destino)

    def test_p4_costos_y_cobertura(self):
        for grafo, costo in ((self.base, 1019), (self.s.aplicar_cierres(), 1033)):
            for inicio in ("N02", "N03"):
                comparacion = self.s.comparar_arboles(inicio, grafo)
                self.assertTrue(comparacion["costos_iguales"])
                for algoritmo in ("prim", "kruskal"):
                    r = comparacion[algoritmo]
                    self.assertEqual(r["costo"], costo)
                    self.comprobar_bosque(grafo, r)

    def test_p5_desconexion(self):
        firma = self.firma(self.base)
        r = self.s.evaluar_desconexion("N24")
        self.assertEqual(sorted(map(len, r["componentes"])), [1, 23])
        self.assertEqual(r["distancia"], math.inf)
        self.assertEqual(r["distancia_floyd"], math.inf)
        self.assertIsNone(r["camino_dijkstra"])
        self.assertIsNone(r["camino_floyd"])
        for algoritmo in ("prim", "kruskal"):
            self.assertTrue(r[algoritmo]["bosque"])
            self.assertEqual(len(r[algoritmo]["aristas"]), 22)
            self.comprobar_bosque(r["grafo"], r[algoritmo])
        self.assertEqual(r["prim"]["costo"], r["kruskal"]["costo"])
        self.assertEqual(self.firma(self.base), firma)

    def test_p7_entradas_invalidas(self):
        with self.assertRaises(KeyError):
            self.s.ruta_minima("N99", "N06")
        with self.assertRaises(KeyError):
            self.s.camino_floyd("N02", "N99")
        with self.assertRaises(KeyError):
            self.s.evaluar_desconexion("N99")
        with self.assertRaises(KeyError):
            self.s.aplicar_cierres((("N01", "N24"),))
        for valor in (0, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                self.s.demo_modificar_peso("N02", "N03", PESO_RUTA, valor)
        with self.assertRaises(TypeError):
            self.s.demo_modificar_peso("N02", "N03", PESO_RED, "10")
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            (carpeta / "vertices.csv").write_text("id,nombre,tipo\nA,Uno,x\nB,Dos,x\n", encoding="utf-8")
            encabezado = "origen,destino,tiempo_entrega_min,costo_enlace_miles_soles\n"
            for fila, error in (("A,B,-1,5\n", ValueError), ("A,B,5\n", ValueError),
                                ("A,Z,2,5\n", KeyError)):
                (carpeta / "aristas.csv").write_text(encabezado + fila, encoding="utf-8")
                with self.assertRaises(error):
                    SistemaEmergencias(carpeta_datos=carpeta)

    def test_p9_desastre_y_base_intacta(self):
        firma = self.firma(self.base)
        r = self.s.ejecutar_escenario()
        g = self.s.grafo_escenario
        self.assertEqual((g.num_vertices, g.num_aristas), (24, 46))
        self.assertTrue(g.es_conexo())
        for a, b in CIERRES_DESASTRE:
            self.assertFalse(g.tiene_arista(a, b))
            self.assertTrue(self.base.tiene_arista(a, b))
        self.assertEqual(self.firma(self.base), firma)
        self.assertEqual(len(r["aumentos"]), 7)
        self.assertEqual(r["inaccesibles"], [])
        self.assertEqual(r["disminuciones"], [])
        self.assertEqual(len(r["antes"]["pares"]), 276)
        self.assertEqual(len(r["despues"]["pares"]), 276)
        self.assertEqual(r["despues"]["rutas"][("N02", "N14")][1], 72)
        self.assertEqual(r["despues"]["rutas"][("N02", "N20")][1], 93)
        self.assertEqual(r["despues"]["prim"]["costo"], 1033)
        self.assertEqual(r["despues"]["kruskal"]["costo"], 1033)
        texto = self.s.texto_escenario()
        self.assertIn("ANTES", texto)
        self.assertIn("DESPUÉS", texto)
        self.assertIn("Aristas:", texto)
        self.assertIn("1033", texto)
        self.s.ejecutar_escenario()
        self.assertEqual(self.s.grafo_escenario.num_aristas, 46)

    def test_exportacion_recargable(self):
        self.s.ejecutar_escenario()
        with tempfile.TemporaryDirectory() as tmp:
            archivos = self.s.exportar_escenario(tmp)
            self.assertTrue(all(r.is_file() for r in archivos.values()))
            g = cargar_grafo(archivos["vertices"], archivos["aristas"])
            self.assertEqual(self.firma(g), self.firma(self.s.grafo_escenario))
            self.assertEqual(set(archivos), {"vertices", "aristas", "tabla", "rutas"})
            with archivos["rutas"].open(encoding="utf-8-sig", newline="") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 8)
            with archivos["tabla"].open(encoding="utf-8-sig", newline="") as f:
                filas = {r["indicador"]: r for r in csv.DictReader(f)}
            self.assertEqual(filas["Conexiones"]["antes"], "48")
            self.assertEqual(filas["Conexiones"]["despues"], "46")
        self.s.aplicar_cierres((("N02", "N08"),))
        with self.assertRaises(ValueError):
            self.s.exportar_escenario()

    def test_demo_pesos_independientes(self):
        firma = self.firma(self.base)
        r = self.s.demo_modificar_peso("N02", "N03", PESO_RUTA, 1)
        self.assertTrue(r["disminuciones"])
        self.assertEqual(r["despues"]["prim"]["costo"], r["antes"]["prim"]["costo"])
        r = self.s.demo_modificar_peso("N02", "N03", PESO_RED, 1)
        self.assertEqual(r["antes"]["pares"], r["despues"]["pares"])
        self.assertLess(r["despues"]["prim"]["costo"], r["antes"]["prim"]["costo"])
        self.assertEqual(self.firma(self.base), firma)

    def test_trazas_y_vulnerabilidad(self):
        self.assertEqual(self.s.ruta_minima("A", "F", self.s.cargar_manual()), (["A", "B", "D", "F"], 27))
        for algoritmo in ("dijkstra", "floyd", "prim", "kruskal"):
            self.assertTrue(self.s.texto_trazas_manuales(algoritmo))
        r = self.s.analizar_falla_mst()
        a, b = map(set, r["grupos"])
        self.assertFalse(a & b)
        self.assertEqual(a | b, set(self.base.ids()))
        mejor = r["mejor_alternativa"]
        self.assertIsNotNone(mejor)
        self.assertTrue((mejor.origen in a and mejor.destino in b) or
                        (mejor.origen in b and mejor.destino in a))

    def test_menu(self):
        self.assertIn("Matriz siguiente (next)", self.s.texto_matriz_floyd())
        self.assertEqual(self.s.texto_rutas_requeridas().count("Coinciden: Sí"), 8)
        salida = io.StringIO()
        with patch("builtins.input", side_effect=["99", "1", "2", "N99", "N06", "0"]):
            with redirect_stdout(salida):
                self.assertEqual(main(), 0)
        texto = salida.getvalue()
        for esperado in ("Opción no válida", "24", "Error:", "Hasta luego"):
            self.assertIn(esperado, texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)