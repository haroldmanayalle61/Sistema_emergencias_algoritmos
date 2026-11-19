import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datos import cargar_grafo_base, cargar_grafo_manual
from kruskal import ConjuntosDisjuntos, Kruskal
from modelo import Arista, Grafo, Vertice
from prim import Prim


class TestConjuntosDisjuntos(unittest.TestCase):
    def test_union_e_ids_desconocidos(self):
        conjuntos = ConjuntosDisjuntos("ABC")
        self.assertTrue(conjuntos.union("A", "B"))
        self.assertFalse(conjuntos.union("B", "A"))
        self.assertFalse(conjuntos.union("C", "C"))
        self.assertEqual(conjuntos.find("A"), conjuntos.find("B"))
        self.assertNotEqual(conjuntos.find("A"), conjuntos.find("C"))
        with self.assertRaises(KeyError):
            conjuntos.find("Z")
        with self.assertRaises(KeyError):
            conjuntos.union("A", "Z")

    def test_rango_y_compresion(self):
        conjuntos = ConjuntosDisjuntos("ABCDEFGH")
        for a, b in [("A", "B"), ("C", "D"), ("E", "F"), ("G", "H"),
                     ("A", "C"), ("E", "G"), ("A", "E")]:
            conjuntos.union(a, b)
        raiz = conjuntos.find("A")
        self.assertEqual(conjuntos._rango[raiz], 3)
        self.assertNotEqual(conjuntos._padre["H"], raiz)
        self.assertEqual(conjuntos.find("H"), raiz)
        self.assertEqual(conjuntos._padre["H"], raiz)
        conjuntos.union("H", "A")
        self.assertEqual(conjuntos._rango[raiz], 3)


class TestKruskal(unittest.TestCase):
    def comprobar_bosque(self, grafo, aristas):
        conjuntos = ConjuntosDisjuntos(grafo.ids())
        for arista in aristas:
            self.assertIs(grafo.obtener_arista(arista.origen, arista.destino), arista)
            self.assertTrue(conjuntos.union(arista.origen, arista.destino))
        grupos = {}
        for codigo in grafo.ids():
            grupos.setdefault(conjuntos.find(codigo), set()).add(codigo)
        self.assertEqual(
            {frozenset(c) for c in grupos.values()},
            {frozenset(c) for c in grafo.componentes_conexas()},
        )

    def test_base_y_escenario_coinciden_con_prim(self):
        base = cargar_grafo_base(RAIZ / "datos")
        escenario = base.copiar()
        escenario.eliminar_arista("N02", "N08")
        escenario.eliminar_arista("N15", "N21")
        for grafo in (base, escenario):
            with self.subTest(aristas=grafo.num_aristas):
                kruskal = Kruskal(grafo)
                aristas, costo = kruskal.calcular_arbol()
                self.comprobar_bosque(grafo, aristas)
                self.assertEqual(len(aristas), 23)
                self.assertEqual(kruskal.cobertura, 24)
                self.assertFalse(kruskal.es_bosque)
                self.assertEqual(costo, sum(a.peso_red for a in aristas))
                for origen in ("N02", "N03"):
                    self.assertEqual(costo, Prim(grafo).calcular_arbol(origen)[1])
        self.assertEqual(base.num_aristas, 48)

    def test_manual_y_traza(self):
        grafo = cargar_grafo_manual(RAIZ / "datos" / "grafo_manual.csv")
        kruskal = Kruskal(grafo, registrar_traza=True)
        aristas, costo = kruskal.calcular_arbol()
        self.comprobar_bosque(grafo, aristas)
        self.assertEqual((len(aristas), costo), (5, 83))
        self.assertEqual(len(kruskal.traza), 9)
        self.assertEqual(sum(p.aceptada for p in kruskal.traza), 5)
        self.assertEqual(kruskal.traza[-1].costo_acumulado, costo)
        for paso in kruskal.traza:
            self.assertEqual(paso.aceptada,
                             paso.representante_origen != paso.representante_destino)
        orden = [(p.arista[2], p.arista[:2]) for p in kruskal.traza]
        self.assertEqual(orden, sorted(orden))
        sin_traza = Kruskal(grafo)
        self.assertEqual(sin_traza.calcular_arbol(), (aristas, costo))
        self.assertEqual(sin_traza.traza, [])

    def test_peso_red_y_empates(self):
        grafo = Grafo()
        for codigo in "ABC":
            grafo.agregar_vertice(Vertice(codigo))
        grafo.agregar_arista(Arista("B", "A", 1, 50))
        grafo.agregar_arista(Arista("C", "B", 10, 2))
        grafo.agregar_arista(Arista("A", "C", 10, 2))
        kruskal = Kruskal(grafo)
        aristas, costo = kruskal.calcular_arbol()
        self.assertEqual({a.clave for a in aristas}, {("A", "C"), ("B", "C")})
        self.assertEqual(costo, 4)
        grafo.obtener_arista("A", "B").peso_red = 2
        aristas, costo = kruskal.calcular_arbol()
        self.comprobar_bosque(grafo, aristas)
        self.assertEqual([a.clave for a in aristas], [("A", "B"), ("A", "C")])
        self.assertEqual(costo, Prim(grafo).calcular_arbol("C")[1])

    def test_desconectado_con_aislado(self):
        grafo = Grafo()
        for codigo in "ABCDE":
            grafo.agregar_vertice(Vertice(codigo))
        grafo.agregar_arista(Arista("A", "B", 1, 2))
        grafo.agregar_arista(Arista("C", "D", 1, 5))
        kruskal = Kruskal(grafo)
        aristas, costo = kruskal.calcular_arbol()
        self.comprobar_bosque(grafo, aristas)
        self.assertEqual((len(aristas), costo, kruskal.cobertura), (2, 7, 5))
        self.assertTrue(kruskal.es_bosque)
        self.assertEqual(len(kruskal.componentes), 3)

    def test_vacio_y_un_vertice(self):
        grafo = Grafo()
        kruskal = Kruskal(grafo)
        self.assertEqual(kruskal.calcular_arbol(), ([], 0))
        self.assertEqual(kruskal.cobertura, 0)
        grafo.agregar_vertice(Vertice("A"))
        self.assertEqual(kruskal.calcular_arbol(), ([], 0))
        self.assertEqual(kruskal.componentes, [["A"]])
        self.assertFalse(kruskal.es_bosque)

    def test_recalculo_reinicia_resultados_y_traza(self):
        grafo = cargar_grafo_manual(RAIZ / "datos" / "grafo_manual.csv")
        kruskal = Kruskal(grafo, registrar_traza=True)
        anteriores, costo_anterior = kruskal.calcular_arbol()
        traza_anterior = kruskal.traza
        grafo.eliminar_vertice("F")
        actuales, costo = kruskal.calcular_arbol()
        self.comprobar_bosque(grafo, actuales)
        self.assertEqual((len(anteriores), costo_anterior, len(traza_anterior)), (5, 83, 9))
        self.assertEqual((len(actuales), costo, kruskal.cobertura), (4, 62, 5))
        self.assertIsNot(anteriores, actuales)
        self.assertEqual(len(kruskal.traza), grafo.num_aristas)

    def test_constructor_invalido(self):
        with self.assertRaises(TypeError):
            Kruskal(None)
        with self.assertRaises(TypeError):
            Kruskal(Grafo(), registrar_traza="si")


if __name__ == "__main__":
    unittest.main(verbosity=2)
