"""Sistema de Emergencias: coordina carga, consultas, algoritmos, escenarios
y exportación. Reutiliza las implementaciones propias del equipo.
Unidades:
- tiempo_entrega_min (peso_ruta): minutos de entrega estimado -> Dijkstra/Floyd.
- costo_enlace_miles_soles (peso_red): miles de soles de enlace -> Prim/Kruskal.
"""
import csv
import math
from pathlib import Path
from datos import cargar_grafo_base, cargar_grafo_manual, exportar_grafo_csv
from dijkstra import Dijkstra
from floyd_warshall import FloydWarshall
from kruskal import Kruskal
from modelo import Grafo, PESO_RED, PESO_RUTA
from prim import Prim
from visualizacion import formatear_traza_prim
RAIZ = Path(__file__).resolve().parents[1]
ORIGENES_RUTAS = ("N02", "N03")
DESTINOS_RUTAS = ("N06", "N10", "N14", "N20")
ALBERGUES = ("N06", "N07", "N08", "N09", "N10")
CIERRES_DESASTRE = (("N02", "N08"), ("N15", "N21"))

# ---------------------------------------------------------------- formato

def _fmt(valor):
    if valor is None:
        return "-"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, (int, float)):
        return "inalcanzable" if valor == math.inf else f"{valor:g}"
    return str(valor)

def _min(valor):
    return "inalcanzable" if valor == math.inf else f"{valor:g} min"

def _camino_texto(camino):
    return "sin camino" if camino is None else " → ".join(camino)

def _num(x):
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    return "∞" if x == math.inf else f"{x:g}"

def _texto_dic(dic):
    partes = []
    for k, v in dic.items():
        if v is None:
            v = "-"
        elif not isinstance(v, str):
            v = _num(v)
        partes.append(f"{k}:{v}")
    return "{" + ", ".join(partes) + "}"

def _texto_matriz(matriz, ids):  # sourcery skip: for-append-to-extend
    filas = ["     " + "".join(f"{i:>5}" for i in ids)]
    for id_fila, fila in zip(ids, matriz):
        filas.append(f"{id_fila:>4} " + "".join(f"{_num(x):>5}" for x in fila))
    return "\n".join(filas)

def _texto_aristas(aristas):
    return ", ".join(f"{a.origen}-{a.destino} ({a.peso_red:g})" for a in aristas) or "ninguna"

class SistemaEmergencias:
    """Fachada del proyecto: la base nunca se modifica; los escenarios usan copias."""

    def __init__(self, carpeta_datos=None, carpeta_resultados=None, grafo_base=None):
        self.carpeta_datos = Path(carpeta_datos) if carpeta_datos is not None else RAIZ / "datos"
        self.carpeta_resultados = (
            Path(carpeta_resultados) if carpeta_resultados is not None else RAIZ / "resultados"
        )
        if grafo_base is not None and not isinstance(grafo_base, Grafo):
            raise TypeError("grafo_base debe ser un Grafo")
        self.grafo_base = grafo_base if grafo_base is not None else cargar_grafo_base(self.carpeta_datos)
        self.grafo_manual = None
        self.grafo_escenario = None
        self.cierres_aplicados = ()
        self.resultado_escenario = None
        self.grafo_demo = None
        self.resultado_demo = None

    # ------------------------------------------------------------ utilidades

    def _g(self, grafo):
        if grafo is None:
            return self.grafo_base
        if not isinstance(grafo, Grafo):
            raise TypeError("se esperaba un objeto Grafo")
        return grafo

    @staticmethod
    def _inicio(grafo):
        if not grafo.ids():
            raise ValueError("El grafo está vacío")
        return "N02" if "N02" in grafo else grafo.ids()[0]

    def cargar_manual(self):
        if self.grafo_manual is None:
            self.grafo_manual = cargar_grafo_manual(self.carpeta_datos / "grafo_manual.csv")
        return self.grafo_manual

    # ------------------------------------------------------------- resumen

    def resumen_base(self):
        g = self.grafo_base
        return {
            "vertices": g.num_vertices,
            "aristas": g.num_aristas,
            "componentes": len(g.componentes_conexas()),
            "conexo": g.es_conexo(),
        }

    def texto_resumen(self):
        r = self.resumen_base()
        return (
            "Grafo base (datos sintéticos)\n"
            f"  Vértices: {r['vertices']}\n"
            f"  Conexiones únicas: {r['aristas']}\n"
            f"  Componentes conexas: {r['componentes']}\n"
            f"  Conexo: {_fmt(r['conexo'])}\n"
            "  Dijkstra/Floyd: tiempo_entrega_min (minutos de entrega estimado)\n"
            "  Prim/Kruskal: costo_enlace_miles_soles (miles de soles de enlace)"
        )

    # ------------------------------------------------------ caminos mínimos

    def ruta_minima(self, origen, destino, grafo=None):
        """Devuelve (camino o None, tiempo en minutos; math.inf si no hay camino)."""
        g = self._g(grafo)
        d = Dijkstra(g)
        distancias, _ = d.calcular_desde(origen)
        camino = d.reconstruir_camino(destino)
        return camino, distancias[destino]

    def rutas_requeridas(self, grafo=None):
        """Ocho rutas: N02 y N03 hacia N06, N10, N14 y N20."""
        g = self._g(grafo)
        rutas = {}
        for origen in ORIGENES_RUTAS:
            if origen not in g:
                continue
            d = Dijkstra(g)
            distancias, _ = d.calcular_desde(origen)
            for destino in DESTINOS_RUTAS:
                if destino in g:
                    rutas[(origen, destino)] = (d.reconstruir_camino(destino), distancias[destino])
        return rutas

    def texto_rutas_requeridas(self, grafo=None):
        g = self._g(grafo)
        fw = FloydWarshall(g)
        matriz, _ = fw.calcular_todos()
        lineas = ["Rutas mínimas (Dijkstra y contraste con Floyd-Warshall, minutos):"]
        for (o, d), (camino, tiempo) in self.rutas_requeridas(g).items():
            tiempo_floyd = matriz[fw.indice[o]][fw.indice[d]]
            lineas.append(f"  {o} → {d}: {_min(tiempo)} · {_camino_texto(camino)}"
                          f" · Floyd: {_min(tiempo_floyd)} · Coinciden: {_fmt(tiempo == tiempo_floyd)}")
        return "\n".join(lineas)

    def albergues_mas_alejados(self, origen="N02", destinos=ALBERGUES, grafo=None):
        g = self._g(grafo)
        d = Dijkstra(g)
        distancias, _ = d.calcular_desde(origen)
        tiempos = {dest: distancias[dest] for dest in destinos}
        maximo = max(tiempos.values())
        return {
            "origen": origen,
            "tiempos": tiempos,
            "ordenados": sorted(tiempos.items(), key=lambda par: (-par[1], par[0])),
            "maximo": maximo,
            "mas_alejados": sorted(dest for dest, t in tiempos.items() if t == maximo),
        }

    def texto_albergues_mas_alejados(self, origen="N02", grafo=None):
        # sourcery skip: for-append-to-extend
        r = self.albergues_mas_alejados(origen, grafo=grafo)
        lineas = [f"Tiempos mínimos desde {origen} a los albergues {ALBERGUES[0]}-{ALBERGUES[-1]}:"]
        for dest, t in r["ordenados"]:
            lineas.append(f"  {dest}: {_min(t)}")
        lineas.append(
            f"Más alejado(s): {', '.join(r['mas_alejados'])} ({_min(r['maximo'])})"
            + (" — empate" if len(r["mas_alejados"]) > 1 else "")
        )
        return "\n".join(lineas)

    def matriz_floyd(self, grafo=None):
        """Devuelve (matriz_distancias, matriz_siguiente, ids)."""
        fw = FloydWarshall(self._g(grafo))
        dist, sig = fw.calcular_todos()
        return dist, sig, fw.ids

    def camino_floyd(self, origen, destino, grafo=None):
        fw = FloydWarshall(self._g(grafo))
        dist, _ = fw.calcular_todos()
        camino = fw.reconstruir_camino(origen, destino)
        return camino, dist[fw.indice[origen]][fw.indice[destino]]

    def texto_matriz_floyd(self, grafo=None):
        dist, sig, ids = self.matriz_floyd(grafo)
        return ("Matriz de distancias Floyd-Warshall (min):\n" + _texto_matriz(dist, ids)
                + "\n\nMatriz siguiente (next):\n" + _texto_matriz(sig, ids))

    # --------------------------------------------------------------- árboles

    def arbol_prim(self, inicio=None, grafo=None):
        g = self._g(grafo)
        inicio = inicio if inicio is not None else self._inicio(g)
        p = Prim(g)
        aristas, costo = p.calcular_arbol(inicio)
        return {
            "algoritmo": "Prim", "inicio": inicio, "aristas": aristas, "costo": costo,
            "cobertura": p.cobertura, "bosque": p.es_bosque, "componentes": p.componentes,
        }

    def arbol_kruskal(self, grafo=None):
        g = self._g(grafo)
        k = Kruskal(g)
        aristas, costo = k.calcular_arbol()
        return {
            "algoritmo": "Kruskal", "inicio": None, "aristas": aristas, "costo": costo,
            "cobertura": k.cobertura, "bosque": k.es_bosque, "componentes": k.componentes,
        }

    def comparar_arboles(self, inicio=None, grafo=None):
        prim = self.arbol_prim(inicio, grafo)
        kruskal = self.arbol_kruskal(grafo)
        return {"prim": prim, "kruskal": kruskal,
                "costos_iguales": math.isclose(prim["costo"], kruskal["costo"])}

    @staticmethod
    def texto_arbol(r):
        tipo = "bosque" if r["bosque"] else "árbol"
        inicio = f" desde {r['inicio']}" if r["inicio"] else ""
        return (
            f"{r['algoritmo']}{inicio} (costo_enlace_miles_soles)\n"
            f"  Resultado: {tipo} · {len(r['aristas'])} aristas · cobertura {r['cobertura']} vértices\n"
            f"  Componentes conexas: {len(r['componentes'])}\n"
            f"  Costo total: {r['costo']:g} miles de soles\n"
            f"  Aristas: {_texto_aristas(r['aristas'])}"
        )

    def texto_comparacion_arboles(self, inicio=None, grafo=None):
        c = self.comparar_arboles(inicio, grafo)
        return (
            self.texto_arbol(c["prim"]) + "\n\n" + self.texto_arbol(c["kruskal"])
            + f"\n\nCostos Prim y Kruskal iguales: {_fmt(c['costos_iguales'])}"
            + "\n(Con empates los árboles pueden diferir, pero el costo óptimo coincide.)"
        )

    # ------------------------------------------------- evaluación y escenarios

    def evaluar(self, grafo=None):
        """Recalcula los cuatro algoritmos sobre un grafo."""
        g = self._g(grafo)
        rutas = self.rutas_requeridas(g)
        fw = FloydWarshall(g)
        matriz, _ = fw.calcular_todos()
        ids = fw.ids
        pares = {}
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pares[(ids[i], ids[j])] = matriz[i][j]
        return {
            "vertices": g.num_vertices,
            "aristas": g.num_aristas,
            "componentes": len(g.componentes_conexas()),
            "rutas": rutas,
            "pares": pares,
            "prim": self.arbol_prim(self._inicio(g), g),
            "kruskal": self.arbol_kruskal(g),
        }

    @staticmethod
    def _inaccesibles(ev):
        return sum(1 for v in ev["pares"].values() if v == math.inf)

    @staticmethod
    def _promedio(ev):
        finitos = [v for v in ev["pares"].values() if v != math.inf]
        return round(sum(finitos) / len(finitos), 2) if finitos else None

    def comparar_grafos(self, antes, despues):
        """Tabla antes/después con rutas afectadas, aumentos y pares inaccesibles."""
        ev0 = self.evaluar(antes)
        ev1 = self.evaluar(despues)
        rutas = []
        for (o, d), (camino0, t0) in ev0["rutas"].items():
            if (o, d) not in ev1["rutas"]:
                continue
            camino1, t1 = ev1["rutas"][(o, d)]
            if t1 == math.inf:
                estado = "inalcanzable"
            elif t1 > t0:
                estado = f"aumento de +{t1 - t0:g} min"
            elif t1 < t0:
                estado = f"disminución de {t0 - t1:g} min"
            else:
                estado = "sin cambio de tiempo"
            rutas.append({
                "origen": o, "destino": d,
                "camino_antes": camino0, "tiempo_antes": t0,
                "camino_despues": camino1, "tiempo_despues": t1,
                "cambia_ruta": camino0 != camino1, "estado": estado,
            })
        aumentos, inaccesibles, disminuciones = [], [], []
        for par, d0 in ev0["pares"].items():
            d1 = ev1["pares"].get(par, math.inf)
            if d0 != math.inf and d1 == math.inf:
                inaccesibles.append((par[0], par[1], d0))
            elif d1 > d0 and d1 != math.inf:
                aumentos.append((par[0], par[1], d0, d1))
            elif d1 < d0 and d0 != math.inf:
                disminuciones.append((par[0], par[1], d0, d1))
        aumentos.sort(key=lambda x: (-(x[3] - x[2]), x[0], x[1]))
        p0, p1, k0, k1 = ev0["prim"], ev1["prim"], ev0["kruskal"], ev1["kruskal"]
        tabla = [
            ("Vértices", ev0["vertices"], ev1["vertices"]),
            ("Conexiones", ev0["aristas"], ev1["aristas"]),
            ("Componentes conexas", ev0["componentes"], ev1["componentes"]),
            ("Pares inaccesibles", self._inaccesibles(ev0), self._inaccesibles(ev1)),
            ("Pares con aumento de tiempo", 0, len(aumentos)),
            ("Pares con disminución de tiempo", 0, len(disminuciones)),
            ("Tiempo medio entre pares alcanzables (min)", self._promedio(ev0), self._promedio(ev1)),
            ("Prim: tipo", "bosque" if p0["bosque"] else "árbol", "bosque" if p1["bosque"] else "árbol"),
            ("Prim: aristas", len(p0["aristas"]), len(p1["aristas"])),
            ("Prim: costo (miles de soles)", p0["costo"], p1["costo"]),
            ("Kruskal: tipo", "bosque" if k0["bosque"] else "árbol", "bosque" if k1["bosque"] else "árbol"),
            ("Kruskal: aristas", len(k0["aristas"]), len(k1["aristas"])),
            ("Kruskal: costo (miles de soles)", k0["costo"], k1["costo"]),
            ("Prim y Kruskal coinciden en costo",
             math.isclose(p0["costo"], k0["costo"]), math.isclose(p1["costo"], k1["costo"])),
        ]
        return {"antes": ev0, "despues": ev1, "rutas": rutas, "aumentos": aumentos,
                "inaccesibles": inaccesibles, "disminuciones": disminuciones,
                "tabla": tabla}

    def aplicar_cierres(self, cierres=CIERRES_DESASTRE):
        """Copia la base y retira las conexiones indicadas. La base no se toca."""
        cierres = tuple(tuple(c) for c in cierres)
        copia = self.grafo_base.copiar()
        for a, b in cierres:
            copia.eliminar_arista(a, b)  # KeyError si no existe
        self.grafo_escenario = copia
        self.cierres_aplicados = cierres
        self.resultado_escenario = None
        return copia

    def ejecutar_escenario(self, cierres=CIERRES_DESASTRE):
        """Retira N02-N08 y N15-N21 (por defecto) y recalcula los cuatro algoritmos."""
        self.aplicar_cierres(cierres)
        self.resultado_escenario = self.comparar_grafos(self.grafo_base, self.grafo_escenario)
        return self.resultado_escenario
    # --- textos del escenario

    @staticmethod
    def texto_tabla(resultado):  # sourcery skip: for-append-to-extend
        filas = resultado["tabla"]
        ancho = max(len(f[0]) for f in filas)
        lineas = [f"{'Indicador':<{ancho}} | {'Antes':>14} | {'Después':>14}", "-" * (ancho + 34)]
        for indicador, antes, despues in filas:
            lineas.append(f"{indicador:<{ancho}} | {_fmt(antes):>14} | {_fmt(despues):>14}")
        return "\n".join(lineas)

    @staticmethod
    def texto_rutas(resultado):  # sourcery skip: merge-list-appends-into-extend
        lineas = ["Rutas requeridas antes → después (tiempo_entrega_min):"]
        for r in resultado["rutas"]:
            lineas.append(
                f"  {r['origen']} → {r['destino']}: {_min(r['tiempo_antes'])} → {_min(r['tiempo_despues'])}"
                f" · {r['estado']}"
                + (" · cambia el camino" if r["cambia_ruta"] else "")
            )
            if r["cambia_ruta"]:
                lineas.append(f"      antes:   {_camino_texto(r['camino_antes'])}")
                lineas.append(f"      después: {_camino_texto(r['camino_despues'])}")
        return "\n".join(lineas)

    @staticmethod
    def texto_pares(resultado, limite=10):  # sourcery skip: for-append-to-extend
        lineas = [
            f"Pares inaccesibles después: {SistemaEmergencias._inaccesibles(resultado['despues'])}",
            f"Pares que perdieron acceso: {len(resultado['inaccesibles'])}",
            f"Pares con disminución finita: {len(resultado['disminuciones'])}",
            f"Pares con aumento finito de tiempo: {len(resultado['aumentos'])}",
        ]
        for a, b, d0, d1 in resultado["aumentos"][:limite]:
            lineas.append(f"  {a}-{b}: {d0:g} → {d1:g} min (+{d1 - d0:g})")
        if len(resultado["aumentos"]) > limite:
            lineas.append(f"  ... y {len(resultado['aumentos']) - limite} más")
        for a, b, d0 in resultado["inaccesibles"][:limite]:
            lineas.append(f"  {a}-{b}: {d0:g} min → inalcanzable")
        for a, b, d0, d1 in resultado["disminuciones"][:limite]:
            lineas.append(f"  {a}-{b}: {d0:g} → {d1:g} min (-{d0 - d1:g})")
        return "\n".join(lineas)

    @staticmethod
    def texto_interpretacion(resultado):
        ev1 = resultado["despues"]
        if resultado["inaccesibles"] or ev1["componentes"] > 1:
            conclusion = (f"La red quedó dividida en {ev1['componentes']} componentes: "
                          f"hay {len(resultado['inaccesibles'])} pares inaccesibles y la expansión mínima es un bosque.")
        else:
            conclusion = ("La red permanece conectada: no hay pérdida de accesibilidad. "
                          f"Pares con aumento: {len(resultado['aumentos'])}; "
                          f"pares con disminución: {len(resultado['disminuciones'])}. "
                          f"Costo de expansión mínima: {resultado['antes']['prim']['costo']:g} → "
                          f"{ev1['prim']['costo']:g} miles de soles.")
        return (conclusion + "\nLímites: datos sintéticos; el modelo no incluye demanda, prioridades "
                "humanitarias, capacidad de caminos ni incertidumbre.")

    def texto_escenario(self, resultado=None):
        r = resultado if resultado is not None else self.resultado_escenario
        if r is None:
            raise ValueError("Primero ejecute el escenario.")
        cierres = ", ".join(f"{a}-{b}" for a, b in self.cierres_aplicados)
        return "\n\n".join([
            f"Escenario: se retiran {cierres} (base intacta, trabajo sobre una copia)",
            self.texto_tabla(r), self.texto_rutas(r), self.texto_pares(r),
            self.texto_arboles_escenario(r), self.texto_interpretacion(r),
        ])

    # ---------------------------------------------------------- exportación

    def exportar_escenario(self, carpeta=None):
        if self.resultado_escenario is None or self.grafo_escenario is None:
            raise ValueError("Primero ejecute el escenario.")
        carpeta = Path(carpeta) if carpeta is not None else self.carpeta_resultados / "escenario"
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta_v, ruta_a = exportar_grafo_csv(self.grafo_escenario, carpeta, prefijo="escenario_")
        ruta_t = carpeta / "tabla_antes_despues.csv"
        with open(ruta_t, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["indicador", "antes", "despues"])
            for indicador, antes, despues in self.resultado_escenario["tabla"]:
                w.writerow([indicador, _fmt(antes), _fmt(despues)])
        ruta_r = carpeta / "rutas_antes_despues.csv"
        with open(ruta_r, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["origen", "destino", "camino_antes", "tiempo_antes_min",
                        "camino_despues", "tiempo_despues_min", "estado"])
            for r in self.resultado_escenario["rutas"]:
                w.writerow([r["origen"], r["destino"], _camino_texto(r["camino_antes"]),
                            _fmt(r["tiempo_antes"]), _camino_texto(r["camino_despues"]),
                            _fmt(r["tiempo_despues"]), r["estado"]])
        return {"vertices": ruta_v, "aristas": ruta_a, "tabla": ruta_t, "rutas": ruta_r}

    # ----------------------------------------------------- demo y desconexión

    def demo_modificar_peso(self, a, b, metrica, valor):
        """Cambia un peso en una COPIA, recalcula todo y compara con la base."""
        if metrica not in (PESO_RUTA, PESO_RED):
            raise ValueError("métrica debe ser 'peso_ruta' o 'peso_red'")
        copia = self.grafo_base.copiar()
        arista = copia.obtener_arista(a, b)
        if arista is None:
            raise KeyError(f"no existe la arista {a}-{b}")
        if metrica == PESO_RUTA:
            arista.peso_ruta = valor
        else:
            arista.peso_red = valor
        self.grafo_demo = copia
        self.resultado_demo = self.comparar_grafos(self.grafo_base, copia)
        return self.resultado_demo

    def evaluar_desconexion(self, id_vertice):
        """P5: aísla un vértice en otra copia (quita todas sus conexiones)."""
        if id_vertice not in self.grafo_base:
            raise KeyError(f"vértice desconocido: {id_vertice}")
        copia = self.grafo_base.copiar()
        for vecino, _ in copia.vecinos(id_vertice):
            copia.eliminar_arista(id_vertice, vecino)
        origen = next((i for i in copia.ids() if i != id_vertice), None)
        if origen is None:
            raise ValueError("Se necesitan al menos dos vértices para esta prueba")
        d = Dijkstra(copia)
        distancias, _ = d.calcular_desde(origen)
        fw = FloydWarshall(copia)
        fw.calcular_todos()
        return {
            "grafo": copia, "aislado": id_vertice, "origen": origen,
            "componentes": copia.componentes_conexas(),
            "distancia": distancias[id_vertice],
            "camino_dijkstra": d.reconstruir_camino(id_vertice),
            "camino_floyd": fw.reconstruir_camino(origen, id_vertice),
            "distancia_floyd": fw.matriz_distancias[fw.indice[origen]][fw.indice[id_vertice]],
            "prim": self.arbol_prim(origen, copia),
            "kruskal": self.arbol_kruskal(copia),
        }

    def texto_desconexion(self, id_vertice):
        r = self.evaluar_desconexion(id_vertice)
        return "\n".join([
            f"Vértice aislado: {r['aislado']} (en una copia; la base sigue intacta)",
            f"Componentes conexas: {len(r['componentes'])}",
            f"Dijkstra {r['origen']} → {r['aislado']}: {_min(r['distancia'])} · {_camino_texto(r['camino_dijkstra'])}",
            f"Floyd {r['origen']} → {r['aislado']}: {_min(r['distancia_floyd'])} · {_camino_texto(r['camino_floyd'])}",
            f"Prim: {'bosque' if r['prim']['bosque'] else 'árbol'} · {len(r['prim']['aristas'])} aristas · "
            f"costo {r['prim']['costo']:g}",
            f"Kruskal: {'bosque' if r['kruskal']['bosque'] else 'árbol'} · {len(r['kruskal']['aristas'])} aristas · "
            f"costo {r['kruskal']['costo']:g}",
        ])

    # --------------------------------------------------------- vulnerabilidad

    @staticmethod
    def _grupos_falla(grafo, aristas_arbol, arista):
        """Grupos que quedan al retirar `arista` del árbol (copia del MST)."""
        arbol = Grafo()
        for v in grafo.vertices():
            arbol.agregar_vertice(v.copiar())
        for a in aristas_arbol:
            if a.clave != arista.clave:
                arbol.agregar_arista(a.copiar())
        grupo_a = grupo_b = None
        for comp in arbol.componentes_conexas():
            if arista.origen in comp:
                grupo_a = sorted(comp)
            if arista.destino in comp:
                grupo_b = sorted(comp)
        return grupo_a, grupo_b

    def _detalle_falla(self, g, aristas, costo, elegida):
        ga, gb = self._grupos_falla(g, aristas, elegida)
        sa, sb = set(ga), set(gb)
        alternativas = sorted(
            (a for a in g.aristas()
             if a.clave != elegida.clave
             and ((a.origen in sa and a.destino in sb) or (a.origen in sb and a.destino in sa))),
            key=lambda a: (a.peso_red, a.clave),
        )
        mejor = alternativas[0] if alternativas else None
        menor = ga if len(ga) <= len(gb) else gb
        return {
            "retirada": elegida,
            "grupos": (ga, gb),
            "afectadas": [(i, g.obtener_vertice(i).nombre) for i in menor],
            "alternativas": alternativas,
            "mejor_alternativa": mejor,
            "costo_original": costo,
            "costo_reconexion": (costo - elegida.peso_red + mejor.peso_red) if mejor else None,
        }

    def analizar_falla_mst(self, conexion=None, grafo=None):
        """Falla de una arista del MST (Kruskal). Sin `conexion` elige la que
        deja los dos grupos más parejos (la más crítica)."""
        g = self._g(grafo)
        aristas, costo = Kruskal(g).calcular_arbol()
        if not aristas:
            raise ValueError("el árbol no tiene aristas")
        if conexion is not None and len(conexion) != 2:
            raise ValueError("La conexión debe contener dos identificadores")
        if conexion is None:
            elegida = max(
                aristas,
                key=lambda a: (min(len(x) for x in self._grupos_falla(g, aristas, a)), a.peso_red),
            )
        else:
            clave = tuple(sorted(conexion))
            elegida = next((a for a in aristas if a.clave == clave), None)
            if elegida is None:
                raise ValueError(f"{clave[0]}-{clave[1]} no pertenece al árbol mínimo")
        return self._detalle_falla(g, aristas, costo, elegida)

    def tabla_vulnerabilidad(self, grafo=None):
        """Una fila por arista del MST: grupos separados y mejor enlace alternativo."""
        g = self._g(grafo)
        aristas, costo = Kruskal(g).calcular_arbol()
        filas = []
        for a in aristas:
            det = self._detalle_falla(g, aristas, costo, a)
            mejor = det["mejor_alternativa"]
            filas.append({
                "arista": a.clave, "peso_red": a.peso_red,
                "tam_grupos": (len(det["grupos"][0]), len(det["grupos"][1])),
                "alternativa": mejor.clave if mejor else None,
                "peso_alternativa": mejor.peso_red if mejor else None,
                "costo_reconexion": det["costo_reconexion"],
            })
        return filas

    def texto_vulnerabilidad(self, conexion=None, grafo=None):
        # sourcery skip: merge-list-appends-into-extend
        r = self.analizar_falla_mst(conexion, grafo)
        a = r["retirada"]
        ga, gb = r["grupos"]
        lineas = [
            f"Falla en el MST: se retira {a.origen}-{a.destino} ({a.peso_red:g} miles de soles)",
            f"  Grupo 1 ({len(ga)}): {', '.join(ga)}",
            f"  Grupo 2 ({len(gb)}): {', '.join(gb)}",
            "  Instalaciones del grupo menor: " + ", ".join(f"{i} ({n})" for i, n in r["afectadas"]),
        ]
        if r["mejor_alternativa"] is None:
            lineas.append("  No hay enlace alternativo en el grafo completo: la red queda dividida.")
        else:
            m = r["mejor_alternativa"]
            lineas.append(f"  Enlaces alternativos en el grafo completo: {len(r['alternativas'])}")
            lineas.append(f"  Mejor alternativa: {m.origen}-{m.destino} ({m.peso_red:g} miles de soles)")
            lineas.append(f"  Costo del árbol: {r['costo_original']:g} → {r['costo_reconexion']:g}")
        return "\n".join(lineas)

    def texto_tabla_vulnerabilidad(self, grafo=None):
        lineas = ["Arista del MST | peso | grupos | mejor alternativa | costo tras reconectar"]
        for f in self.tabla_vulnerabilidad(grafo):
            alt = "-" if f["alternativa"] is None else f"{f['alternativa'][0]}-{f['alternativa'][1]} ({f['peso_alternativa']:g})"
            rec = "-" if f["costo_reconexion"] is None else f"{f['costo_reconexion']:g}"
            lineas.append(f"{f['arista'][0]}-{f['arista'][1]} | {f['peso_red']:g} | "
                          f"{f['tam_grupos'][0]}/{f['tam_grupos'][1]} | {alt} | {rec}")
        return "\n".join(lineas)

    # ------------------------------------------------------- trazas manuales

    def texto_traza_dijkstra_manual(self, origen="A", destino="F"):
        g = self.cargar_manual()
        d = Dijkstra(g, registrar_traza=True)
        distancias, _ = d.calcular_desde(origen)
        lineas = [f"Dijkstra manual desde {origen} (tiempo_entrega_min)"]
        for ev in d.traza:
            if ev["evento"] == "extraccion":
                nota = " (entrada antigua, se descarta)" if ev["descartada"] else ""
                lineas.append(f"Extrae {ev['vertice']} con d={_num(ev['distancia'])}{nota}")
                lineas.append(f"    distancias:   {_texto_dic(ev['distancias'])}")
                lineas.append(f"    predecesores: {_texto_dic(ev['predecesores'])}")
            else:
                lineas.append(
                    f"  Relaja {ev['origen']}→{ev['destino']}: "
                    f"{_num(ev['distancia_anterior'])} → {_num(ev['distancia_nueva'])}"
                )
        lineas.append(f"Camino {origen}→{destino}: {_camino_texto(d.reconstruir_camino(destino))} "
                      f"({_min(distancias[destino])})")
        return "\n".join(lineas)

    def texto_traza_floyd_manual(self, origen="A", destino="F"):
        g = self.cargar_manual()
        fw = FloydWarshall(g, registrar_traza=True)
        matriz, _ = fw.calcular_todos()
        ids = fw.ids
        lineas = ["Floyd-Warshall manual (tiempo_entrega_min)", "", "Matriz inicial:",
                  _texto_matriz(fw.traza[0]["matriz_distancias"], ids)]
        pasos = fw.traza[1:]
        for n, paso in enumerate(pasos, start=1):
            final = " (matriz final)" if n == len(pasos) else ""
            lineas += ["", f"Tras usar {paso['intermedio']} como intermedio{final}:",
                       _texto_matriz(paso["matriz_distancias"], ids)]
        camino = fw.reconstruir_camino(origen, destino)
        dist = matriz[fw.indice[origen]][fw.indice[destino]]
        lineas += ["", f"Consulta {origen}→{destino}: {_camino_texto(camino)} ({_min(dist)})"]
        return "\n".join(lineas)

    def texto_traza_prim_manual(self, inicio="A"):
        g = self.cargar_manual()
        p = Prim(g, registrar_traza=True)
        aristas, costo = p.calcular_arbol(inicio)
        return "\n".join([
            f"Prim manual desde {inicio} (costo_enlace_miles_soles)",
            formatear_traza_prim(p.traza),
            f"Resultado: {_texto_aristas(aristas)} · costo {costo:g}",
        ])

    def texto_traza_kruskal_manual(self):
        g = self.cargar_manual()
        k = Kruskal(g, registrar_traza=True)
        aristas, costo = k.calcular_arbol()
        necesarias = g.num_vertices - len(k.componentes)
        aceptadas = 0
        lineas = ["Kruskal manual (costo_enlace_miles_soles), aristas en orden:"]
        for n, paso in enumerate(k.traza, start=1):
            a, b, peso = paso.arista
            if paso.aceptada:
                decision = "ACEPTADA (une componentes distintas)"
                aceptadas += 1
            elif aceptadas == necesarias:
                decision = "RECHAZADA (cierra ciclo; el árbol ya estaba completo)"
            else:
                decision = "RECHAZADA (cierra ciclo)"
            lineas.append(
                f"{n}. {a}-{b} ({peso:g}) · representantes {paso.representante_origen}/"
                f"{paso.representante_destino} · {decision} · costo acumulado {paso.costo_acumulado:g}"
            )
        lineas.append(f"Resultado: {_texto_aristas(aristas)} · costo {costo:g}")
        return "\n".join(lineas)

    def texto_trazas_manuales(self, algoritmo="todos"):
        opciones = {
            "dijkstra": self.texto_traza_dijkstra_manual,
            "floyd": self.texto_traza_floyd_manual,
            "prim": self.texto_traza_prim_manual,
            "kruskal": self.texto_traza_kruskal_manual,
        }
        algoritmo = algoritmo.lower()
        if algoritmo == "todos":
            return "\n\n".join(f() for f in opciones.values())
        if algoritmo not in opciones:
            raise ValueError("algoritmo debe ser dijkstra, floyd, prim, kruskal o todos")
        return opciones[algoritmo]()


    @staticmethod
    def texto_arboles_escenario(resultado):
        # sourcery skip: for-append-to-extend
        lineas = []
        for etapa in ("antes", "despues"):
            lineas.append("ANTES" if etapa == "antes" else "DESPUÉS")
            for algoritmo in ("prim", "kruskal"):
                lineas.append(SistemaEmergencias.texto_arbol(resultado[etapa][algoritmo]))
        return "\n".join(lineas)