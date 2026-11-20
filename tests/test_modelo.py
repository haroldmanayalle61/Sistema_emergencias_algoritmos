import math
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from modelo import Arista, Grafo, Vertice
import datos

DATOS = RAIZ / "datos"


def grafo_triangulo():
    g = Grafo()
    for i in "ABC":
        g.agregar_vertice(Vertice(i, f"nodo {i}", "prueba"))
    g.agregar_arista(Arista("A", "B", 1, 10))
    g.agregar_arista(Arista("B", "C", 2, 20))
    g.agregar_arista(Arista("A", "C", 4, 30))
    return g


class TestVerticeArista(unittest.TestCase):
    def test_igualdad_por_id(self):
        self.assertEqual(Vertice("N01", "uno"), Vertice("N01", "otro nombre"))
        self.assertNotEqual(Vertice("N01"), Vertice("N02"))
        self.assertEqual(len({Vertice("N01"), Vertice("N01")}), 1)

    def test_metadatos_encapsulados(self):
        v = Vertice("N01", metadatos={"x": 1})
        v.metadatos["x"] = 99
        self.assertEqual(v.metadatos["x"], 1)

    def test_metadatos_anidados_independientes_de_entrada_y_consulta(self):
        originales = {"detalle": {"coordenadas": [11, -1]}}
        vertice = Vertice("A", metadatos=originales)
        arista = Arista("A", "B", 1, 2, metadatos=originales)
        originales["detalle"]["coordenadas"][0] = 50

        for objeto in (vertice, arista):
            with self.subTest(tipo=type(objeto).__name__):
                consulta = objeto.metadatos
                self.assertEqual(consulta["detalle"]["coordenadas"], [11, -1])
                consulta["detalle"]["coordenadas"].append(99)
                self.assertEqual(objeto.metadatos["detalle"]["coordenadas"], [11, -1])
                copia = objeto.copiar()
                self.assertIsNot(copia._metadatos["detalle"], objeto._metadatos["detalle"])
                self.assertIsNot(
                    copia._metadatos["detalle"]["coordenadas"],
                    objeto._metadatos["detalle"]["coordenadas"],
                )

    def test_tipos_y_valores_invalidos(self):
        with self.assertRaises(TypeError):
            Vertice(5)
        with self.assertRaises(ValueError):
            Vertice("  ")
        with self.assertRaises(TypeError):
            Arista("A", "B", "3", 4)
        for malo in (0, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                Arista("A", "B", malo, 4)
        with self.assertRaises(ValueError):
            Arista("A", "A", 1, 1)

    def test_clave_sin_direccion_y_pesos_separados(self):
        a = Arista("N02", "N01", 20, 52)
        self.assertEqual(a.clave, ("N01", "N02"))
        self.assertEqual(a.peso("peso_ruta"), 20)
        self.assertEqual(a.peso("peso_red"), 52)
        self.assertEqual(a.otro_extremo("N02"), "N01")
        with self.assertRaises(ValueError):
            a.peso("otra")
        with self.assertRaises(KeyError):
            a.otro_extremo("N99")

    def test_setter_valida(self):
        a = Arista("A", "B", 1, 1)
        a.peso_ruta = 9
        self.assertEqual(a.peso_ruta, 9)
        with self.assertRaises(ValueError):
            a.peso_red = -3


class TestGrafo(unittest.TestCase):
    def test_altas_y_errores(self):
        g = grafo_triangulo()
        self.assertEqual((g.num_vertices, g.num_aristas), (3, 3))
        with self.assertRaises(ValueError):
            g.agregar_vertice(Vertice("A"))
        with self.assertRaises(ValueError):
            g.agregar_arista(Arista("B", "A", 5, 5))     # inversa de A-B
        with self.assertRaises(KeyError):
            g.agregar_arista(Arista("A", "Z", 1, 1))
        with self.assertRaises(TypeError):
            g.agregar_vertice("A")
        with self.assertRaises(KeyError):
            g.vecinos("Z")

    def test_vecinos_ambos_sentidos_misma_arista(self):
        g = grafo_triangulo()
        self.assertIs(g.obtener_arista("A", "B"), g.obtener_arista("B", "A"))
        pares = dict(g.vecinos("B"))
        self.assertEqual(set(pares), {"A", "C"})
        self.assertEqual(pares["A"].peso_ruta, 1)

    def test_aristas_unicas(self):
        g = grafo_triangulo()
        self.assertEqual(len(g.aristas()), 3)
        self.assertEqual(len({a.clave for a in g.aristas()}), 3)

    def test_eliminar_vertice_quita_conexiones(self):
        g = grafo_triangulo()
        g.eliminar_vertice("B")
        self.assertEqual((g.num_vertices, g.num_aristas), (2, 1))
        self.assertNotIn("B", dict(g.vecinos("A")))
        with self.assertRaises(KeyError):
            g.eliminar_vertice("B")

    def test_eliminar_arista(self):
        g = grafo_triangulo()
        quitada = g.eliminar_arista("C", "B")
        self.assertEqual(quitada.clave, ("B", "C"))
        self.assertFalse(g.tiene_arista("B", "C"))
        self.assertEqual(g.num_aristas, 2)
        with self.assertRaises(KeyError):
            g.eliminar_arista("B", "C")

    def test_copia_independiente(self):
        g = grafo_triangulo()
        c = g.copiar()
        c.eliminar_vertice("A")
        c.obtener_arista("B", "C").peso_ruta = 99
        self.assertEqual((g.num_vertices, g.num_aristas), (3, 3))
        self.assertEqual(g.obtener_arista("B", "C").peso_ruta, 2)

    def test_copia_grafo_con_metadatos_anidados(self):
        g = Grafo()
        g.agregar_vertice(Vertice("A", metadatos={"detalle": {"valores": [1]}}))
        g.agregar_vertice(Vertice("B"))
        g.agregar_arista(Arista("A", "B", 1, 2, {"detalle": {"valores": [3]}}))
        copia = g.copiar()

        # Se inspecciona el almacenamiento para verificar la independencia real.
        copia.obtener_vertice("A")._metadatos["detalle"]["valores"].append(2)
        copia.obtener_arista("A", "B")._metadatos["detalle"]["valores"].append(4)
        self.assertEqual(g.obtener_vertice("A").metadatos["detalle"]["valores"], [1])
        self.assertEqual(g.obtener_arista("A", "B").metadatos["detalle"]["valores"], [3])
        self.assertIs(copia.obtener_arista("A", "B"), copia.obtener_arista("B", "A"))

    def test_peso_y_ausencia(self):
        g = grafo_triangulo()
        g.agregar_vertice(Vertice("D"))
        self.assertEqual(g.peso("A", "C", "peso_red"), 30)
        self.assertEqual(g.peso("C", "A", "peso_ruta"), 4)
        self.assertEqual(g.peso("A", "D", "peso_ruta"), math.inf)

    def test_matriz_diagonal_infinito_simetria(self):
        g = grafo_triangulo()
        g.agregar_vertice(Vertice("D"))
        m, ids = g.a_matriz_adyacencia("peso_ruta")
        self.assertEqual(ids, ["A", "B", "C", "D"])
        for i in range(4):
            self.assertEqual(m[i][i], 0)
            for j in range(4):
                self.assertEqual(m[i][j], m[j][i])
        self.assertEqual(m[0][1], 1)
        self.assertEqual(m[0][3], math.inf)
        m2, _ = g.a_matriz_adyacencia("peso_red")
        self.assertEqual(m2[0][1], 10)          # métricas no se mezclan

    def test_lista_adyacencia(self):
        la = grafo_triangulo().a_lista_adyacencia("peso_red")
        self.assertEqual(sorted(la["A"]), [("B", 10), ("C", 30)])
        with self.assertRaises(ValueError):
            grafo_triangulo().a_lista_adyacencia("x")

    def test_conectividad_y_componentes(self):
        g = grafo_triangulo()
        self.assertTrue(g.es_conexo())
        g.agregar_vertice(Vertice("D"))
        self.assertFalse(g.es_conexo())
        self.assertEqual(len(g.componentes_conexas()), 2)


class TestCargaBase(unittest.TestCase):
    """P1: 24 nodos, 48 aristas únicas, simetría, pesos positivos, conectividad."""

    @classmethod
    def setUpClass(cls):
        cls.g = datos.cargar_grafo_base(DATOS)

    def test_tamano(self):
        self.assertEqual(self.g.num_vertices, 24)
        self.assertEqual(self.g.num_aristas, 48)
        self.assertEqual(len({a.clave for a in self.g.aristas()}), 48)

    def test_conexo(self):
        self.assertTrue(self.g.es_conexo())

    def test_pesos_positivos_y_finitos(self):
        for a in self.g.aristas():
            for p in (a.peso_ruta, a.peso_red):
                self.assertTrue(math.isfinite(p) and p > 0)

    def test_simetria_matrices(self):
        for metrica in ("peso_ruta", "peso_red"):
            m, ids = self.g.a_matriz_adyacencia(metrica)
            self.assertEqual(len(ids), 24)
            for i in range(24):
                self.assertEqual(m[i][i], 0)
                for j in range(24):
                    self.assertEqual(m[i][j], m[j][i])
            finitas = sum(1 for i in range(24) for j in range(i + 1, 24) if m[i][j] != math.inf)
            self.assertEqual(finitas, 48)

    def test_lista_y_matriz_coinciden(self):
        la = self.g.a_lista_adyacencia("peso_ruta")
        m, ids = self.g.a_matriz_adyacencia("peso_ruta")
        for i, id_v in enumerate(ids):
            desde_matriz = {ids[j] for j in range(24) if j != i and m[i][j] != math.inf}
            self.assertEqual({v for v, _ in la[id_v]}, desde_matriz)

    def test_datos_conocidos(self):
        self.assertEqual(self.g.obtener_vertice("N02").nombre, "Almacén Humanitario Norte")
        self.assertEqual(self.g.obtener_vertice("N01").rol, "instalación")
        self.assertEqual(self.g.obtener_vertice("N02").metadatos["x_esquema"], 11.0)
        self.assertEqual(self.g.peso("N01", "N02", "peso_ruta"), 20)
        self.assertEqual(self.g.peso("N02", "N01", "peso_red"), 52)

    def test_escenario_cierres_sobre_copia(self):
        copia = self.g.copiar()
        r1 = copia.eliminar_arista("N02", "N08")
        r2 = copia.eliminar_arista("N21", "N15")      # sentido inverso también funciona
        self.assertEqual({r1.clave, r2.clave}, {("N02", "N08"), ("N15", "N21")})
        self.assertEqual(copia.num_aristas, 46)
        self.assertEqual(copia.num_vertices, 24)
        self.assertTrue(copia.es_conexo())
        # base intacta
        self.assertEqual(self.g.num_aristas, 48)
        self.assertTrue(self.g.tiene_arista("N02", "N08"))
        self.assertTrue(self.g.tiene_arista("N15", "N21"))

    def test_p5_aislar_un_vertice(self):
        copia = self.g.copiar()
        for vecino, _ in copia.vecinos("N24"):
            copia.eliminar_arista("N24", vecino)
        self.assertFalse(copia.es_conexo())
        self.assertEqual(sorted(len(c) for c in copia.componentes_conexas()), [1, 23])


class TestGrafoManual(unittest.TestCase):
    def test_a_f(self):
        g = datos.cargar_grafo_manual(DATOS / "grafo_manual.csv")
        self.assertEqual(g.ids(), list("ABCDEF"))
        self.assertEqual(g.num_aristas, 9)
        self.assertTrue(g.es_conexo())
        self.assertEqual(g.peso("A", "B", "peso_ruta"), 7)
        self.assertEqual(g.peso("A", "B", "peso_red"), 9)
        self.assertEqual(g.peso("E", "F", "peso_red"), 21)


class TestErroresCSV(unittest.TestCase):
    """P7: CSV defectuoso, faltantes, ids desconocidos, pesos negativos."""

    ENC_V = "id,nombre,tipo,x_esquema,y_esquema\n"
    ENC_A = "origen,destino,tiempo_entrega_min,costo_enlace_miles_soles\n"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        (self.dir / "v.csv").write_text(
            self.ENC_V + "N01,Uno,instalación,0,0\nN02,Dos,instalación,1,1\n", encoding="utf-8")

    def aristas(self, cuerpo):
        ruta = self.dir / "a.csv"
        ruta.write_text(self.ENC_A + cuerpo, encoding="utf-8")
        return ruta

    def cargar(self, cuerpo):
        return datos.cargar_grafo(self.dir / "v.csv", self.aristas(cuerpo))

    def test_valido(self):
        self.assertEqual(self.cargar("N01,N02,5,9\n").num_aristas, 1)

    def test_campo_faltante_informa_archivo_y_fila(self):
        with self.assertRaises(datos.ErrorCargaCSV) as cm:
            self.cargar("N01,N02,5,9\nN01,N02,5\n")
        self.assertIn("a.csv", str(cm.exception))
        self.assertEqual(cm.exception.fila, 3)

    def test_no_numerico(self):
        with self.assertRaises(datos.ErrorCargaCSV) as cm:
            self.cargar("N01,N02,cinco,9\n")
        self.assertIn("no numérico", str(cm.exception))
        self.assertEqual(cm.exception.fila, 2)

    def test_pesos_invalidos(self):
        for malo in ("-4", "0", "nan", "inf"):
            with self.assertRaises(ValueError, msg=malo):
                self.cargar(f"N01,N02,{malo},9\n")

    def test_id_desconocido_es_keyerror(self):
        with self.assertRaises(KeyError) as cm:
            self.cargar("N01,N99,5,9\n")
        self.assertIn("N99", str(cm.exception))
        self.assertEqual(cm.exception.fila, 2)

    def test_duplicado_e_inverso(self):
        with self.assertRaises(datos.ErrorCargaCSV) as cm:
            self.cargar("N01,N02,5,9\nN02,N01,5,9\n")
        self.assertIn("duplicada", str(cm.exception))
        self.assertEqual(cm.exception.fila, 3)
        with self.assertRaises(datos.ErrorCargaCSV):
            self.cargar("N01,N02,5,9\nN01,N02,6,8\n")

    def test_lazo_y_encabezado_incompleto(self):
        with self.assertRaises(datos.ErrorCargaCSV):
            self.cargar("N01,N01,5,9\n")
        ruta = self.dir / "mal.csv"
        ruta.write_text("origen,destino,tiempo_entrega_min\nN01,N02,5\n", encoding="utf-8")
        with self.assertRaises(datos.ErrorCargaCSV) as cm:
            datos.cargar_aristas(ruta)
        self.assertIn("falta la columna", str(cm.exception))

    def test_vertice_duplicado_y_vacio(self):
        ruta = self.dir / "vd.csv"
        ruta.write_text(self.ENC_V + "N01,Uno,x,0,0\nN01,Otro,x,1,1\n", encoding="utf-8")
        with self.assertRaises(datos.ErrorCargaCSV) as cm:
            datos.cargar_vertices(ruta)
        self.assertEqual(cm.exception.fila, 3)
        ruta.write_text(self.ENC_V + "N01,,x,0,0\n", encoding="utf-8")
        with self.assertRaises(datos.ErrorCargaCSV):
            datos.cargar_vertices(ruta)

    def test_coordenada_no_numerica(self):
        ruta = self.dir / "vc.csv"
        ruta.write_text(self.ENC_V + "N01,Uno,x,abc,0\n", encoding="utf-8")
        with self.assertRaises(datos.ErrorCargaCSV):
            datos.cargar_vertices(ruta)

    def test_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            datos.cargar_vertices(self.dir / "no_existe.csv")

    def test_tipo_opcional_en_aristas_se_conserva(self):
        ruta = self.dir / "t.csv"
        ruta.write_text("origen,destino,peso_ruta,peso_red,tipo\nA,B,1,2,principal\n", encoding="utf-8")
        self.assertEqual(datos.cargar_aristas(ruta)[0].metadatos["tipo"], "principal")


class TestExportar(unittest.TestCase):
    def test_ida_y_vuelta(self):
        g = datos.cargar_grafo_base(DATOS)
        with tempfile.TemporaryDirectory() as tmp:
            rv, ra = datos.exportar_grafo_csv(g, tmp, "mod_")
            h = datos.cargar_grafo(rv, ra)
        self.assertEqual((h.num_vertices, h.num_aristas), (24, 48))
        for a in g.aristas():
            self.assertEqual(h.peso(a.origen, a.destino, "peso_ruta"), a.peso_ruta)
            self.assertEqual(h.peso(a.origen, a.destino, "peso_red"), a.peso_red)


class TestGeneradores(unittest.TestCase):
    def firma(self, g):
        return sorted((a.clave, a.peso_ruta, a.peso_red) for a in g.aristas())

    def test_cuatro_configuraciones(self):
        esperado = {"100_disperso": (100, 200), "100_denso": (100, 1238),
                    "200_disperso": (200, 400), "200_denso": (200, 4975)}
        for nombre, (v, e) in esperado.items():
            g = datos.generar_configuracion(nombre)
            self.assertEqual((g.num_vertices, g.num_aristas), (v, e), nombre)
            self.assertTrue(g.es_conexo(), nombre)
            for a in g.aristas():
                self.assertGreater(a.peso_ruta, 0)
                self.assertGreater(a.peso_red, 0)
            self.assertEqual(len({a.clave for a in g.aristas()}), e)

    def test_reproducible_y_semilla_distinta(self):
        a = self.firma(datos.generar_grafo(50, 120, semilla=7))
        b = self.firma(datos.generar_grafo(50, 120, semilla=7))
        c = self.firma(datos.generar_grafo(50, 120, semilla=8))
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_arbol_minimo_de_conectividad(self):
        g = datos.generar_grafo(30, 29)               # exactamente un árbol
        self.assertEqual(g.num_aristas, 29)
        self.assertTrue(g.es_conexo())

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            datos.generar_grafo(10, 5)                # no alcanza para conexo
        with self.assertRaises(ValueError):
            datos.generar_grafo(10, 46)               # más que el completo (45)
        with self.assertRaises(TypeError):
            datos.generar_grafo(10.0, 20)
        with self.assertRaises(KeyError):
            datos.generar_configuracion("300_denso")


if __name__ == "__main__":
    unittest.main(verbosity=2)
    
    
