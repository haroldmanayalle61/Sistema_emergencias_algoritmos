from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datos import cargar_grafo_base, cargar_grafo_manual  # noqa: E402
from modelo import Arista, Grafo, Vertice  # noqa: E402
from prim import Prim  # noqa: E402
from visualizacion import formatear_traza_prim  # noqa: E402

DATOS = RAIZ / "datos"


def grafo_con_empates() -> Grafo:
    grafo = Grafo()
    for id_vertice in "ABC":
        grafo.agregar_vertice(Vertice(id_vertice, id_vertice, "prueba"))
    grafo.agregar_arista(Arista("A", "B", 8, 1))
    grafo.agregar_arista(Arista("B", "C", 9, 1))
    grafo.agregar_arista(Arista("A", "C", 10, 1))
    return grafo


def comprobar_arbol(test: unittest.TestCase, grafo: Grafo, aristas: list[Arista]) -> None:
    """Comprueba V-1, ausencia de ciclos y conectividad del resultado."""
    ids = grafo.ids()
    test.assertEqual(len(aristas), max(0, len(ids) - 1))
    padre = {id_vertice: id_vertice for id_vertice in ids}

    def raiz(id_vertice: str) -> str:
        while padre[id_vertice] != id_vertice:
            padre[id_vertice] = padre[padre[id_vertice]]
            id_vertice = padre[id_vertice]
        return id_vertice

    for arista in aristas:
        raiz_a, raiz_b = raiz(arista.origen), raiz(arista.destino)
        test.assertNotEqual(raiz_a, raiz_b, f"la arista {arista.clave} cerraría un ciclo")
        padre[raiz_a] = raiz_b

    if ids:
        test.assertEqual(len({raiz(id_vertice) for id_vertice in ids}), 1)


class TestPrim(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grafo_base = cargar_grafo_base(DATOS)
        cls.grafo_manual = cargar_grafo_manual(DATOS / "grafo_manual.csv")

    def test_base_desde_n02_y_n03_cubre_24_con_23_aristas(self) -> None:
        prim_n02 = Prim(self.grafo_base)
        aristas_n02, costo_n02 = prim_n02.calcular_arbol("N02")
        comprobar_arbol(self, self.grafo_base, aristas_n02)
        self.assertEqual(prim_n02.cobertura, 24)
        self.assertEqual(len(aristas_n02), 23)
        self.assertFalse(prim_n02.es_bosque)
        self.assertAlmostEqual(costo_n02, sum(a.peso("peso_red") for a in aristas_n02))

        prim_n03 = Prim(self.grafo_base)
        aristas_n03, costo_n03 = prim_n03.calcular_arbol("N03")
        comprobar_arbol(self, self.grafo_base, aristas_n03)
        self.assertEqual(prim_n03.cobertura, 24)
        self.assertEqual(len(aristas_n03), 23)
        self.assertAlmostEqual(costo_n02, costo_n03)

    def test_usa_peso_red_y_no_peso_ruta(self) -> None:
        grafo = Grafo()
        for id_vertice in "ABC":
            grafo.agregar_vertice(Vertice(id_vertice))
        grafo.agregar_arista(Arista("A", "B", 1, 50))
        grafo.agregar_arista(Arista("B", "C", 1, 2))
        grafo.agregar_arista(Arista("A", "C", 100, 3))

        prim = Prim(grafo)
        aristas, costo = prim.calcular_arbol("A")

        self.assertEqual({a.clave for a in aristas}, {("A", "C"), ("B", "C")})
        self.assertEqual(costo, 5.0)

    def test_caso_manual_desde_a_y_traza(self) -> None:
        prim = Prim(self.grafo_manual, registrar_traza=True)
        aristas, costo = prim.calcular_arbol("A")

        comprobar_arbol(self, self.grafo_manual, aristas)
        self.assertEqual(len(aristas), 5)
        self.assertEqual(costo, 83.0)
        self.assertTrue(prim.traza)
        self.assertEqual(prim.traza[0].vertice_agregado, "A")
        self.assertTrue(any(p.arista_elegida is not None for p in prim.traza))
        texto = formatear_traza_prim(prim.traza)
        self.assertIn("Frontera:", texto)
        self.assertIn("Arista elegida:", texto)
        self.assertIn("Vértice incorporado:", texto)
        self.assertIn("Costo acumulado:", texto)

    def test_empates_producen_un_arbol_valido_de_costo_optimo(self) -> None:
        grafo = grafo_con_empates()
        prim = Prim(grafo)
        aristas, costo = prim.calcular_arbol("A")

        comprobar_arbol(self, grafo, aristas)
        self.assertEqual(costo, 2.0)
        self.assertEqual(len(aristas), 2)

    def test_grafo_desconectado_devuelve_bosque_y_cubre_todos(self) -> None:
        grafo = Grafo()
        for id_vertice in "ABCDE":
            grafo.agregar_vertice(Vertice(id_vertice))
        grafo.agregar_arista(Arista("A", "B", 1, 2))
        grafo.agregar_arista(Arista("C", "D", 1, 5))

        prim = Prim(grafo)
        aristas, costo = prim.calcular_arbol("C")

        self.assertEqual(len(aristas), 2)
        self.assertEqual(costo, 7.0)
        self.assertEqual(prim.cobertura, 5)
        self.assertEqual(len(prim.componentes), 3)
        self.assertTrue(prim.es_bosque)
        self.assertEqual({frozenset(c) for c in prim.componentes}, {
            frozenset({"A", "B"}), frozenset({"C", "D"}), frozenset({"E"})
        })

    def test_id_inexistente_y_reutilizacion_reinician_resultados(self) -> None:
        prim = Prim(self.grafo_base)
        with self.assertRaises(KeyError):
            prim.calcular_arbol("N99")

        primera, costo_primera = prim.calcular_arbol("N02")
        segunda, costo_segunda = prim.calcular_arbol("N03")
        self.assertEqual(len(primera), 23)
        self.assertEqual(len(segunda), 23)
        self.assertEqual(prim.inicio_actual, "N03")
        self.assertAlmostEqual(costo_primera, costo_segunda)


if __name__ == "__main__":
    unittest.main(verbosity=2)
