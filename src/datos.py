
import csv
import math
import random
from pathlib import Path

from modelo import Arista, Grafo, Vertice

# encabezados aceptados en el CSV
ALIAS_PESOS = {
    "peso_ruta": ("peso_ruta", "tiempo_entrega_min"),
    "peso_red": ("peso_red", "costo_enlace_miles_soles"),
}
COLUMNAS_VERTICE = ("id", "nombre", "tipo")


class ErrorCargaCSV(ValueError):
    def __init__(self, archivo, fila, detalle):
        self.archivo = Path(archivo).name
        self.fila = fila
        self.detalle = detalle
        ubicacion = "encabezado" if fila is None else f"fila {fila}"
        super().__init__(f"{self.archivo}, {ubicacion}: {detalle}")


class IdDesconocidoCSV(KeyError):
    def __init__(self, archivo, fila, detalle):
        self.archivo = Path(archivo).name
        self.fila = fila
        self.detalle = detalle
        self.mensaje = f"{self.archivo}, fila {fila}: {detalle}"
        super().__init__(self.mensaje)

    def __str__(self):
        return self.mensaje


# lectura
def _leer_filas(ruta, columnas):
    """Devuelve (mapa_columnas, filas) con filas = [(n_fila, dict_original)].
    """
    ruta = Path(ruta)
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        if not lector.fieldnames:
            raise ErrorCargaCSV(ruta, None, "el archivo está vacío o no tiene encabezado")
        encabezados = [h.strip() for h in lector.fieldnames]
        lector.fieldnames = encabezados
        mapa = {}
        for col in columnas:
            candidatos = ALIAS_PESOS.get(col, (col,))
            hallado = next((c for c in candidatos if c in encabezados), None)
            if hallado is None:
                raise ErrorCargaCSV(ruta, None, f"falta la columna '{col}'"
                                    + (f" (o {candidatos[1]})" if col in ALIAS_PESOS else ""))
            mapa[col] = hallado
        filas = []
        for fila in lector:
            n_fila = lector.line_num
            if None in fila:
                raise ErrorCargaCSV(ruta, n_fila, "tiene más campos que el encabezado")
            filas.append((n_fila, fila))
    return mapa, filas


def _texto_obligatorio(ruta, n_fila, fila, columna):
    valor = fila.get(columna)
    if valor is None or not valor.strip():
        raise ErrorCargaCSV(ruta, n_fila, f"campo faltante o vacío: '{columna}'")
    return valor.strip()


def _numero(ruta, n_fila, texto, columna):
    try:
        return int(texto)
    except ValueError:
        pass
    try:
        valor = float(texto)
    except ValueError:
        raise ErrorCargaCSV(ruta, n_fila, f"valor no numérico en '{columna}': {texto!r}") from None
    if not math.isfinite(valor):
        raise ErrorCargaCSV(ruta, n_fila, f"valor no finito en '{columna}': {texto!r}")
    return valor


def _peso(ruta, n_fila, texto, columna):
    valor = _numero(ruta, n_fila, texto, columna)
    if valor <= 0:
        raise ErrorCargaCSV(ruta, n_fila, f"'{columna}' debe ser positivo, se leyó {valor}")
    return valor


def cargar_vertices(ruta):
    """Lee vertices.csv -> lista de Vertice (tipo -> rol; resto -> metadatos)."""
    mapa, filas = _leer_filas(ruta, COLUMNAS_VERTICE)
    vistos = {}
    resultado = []
    for n_fila, fila in filas:
        id_v = _texto_obligatorio(ruta, n_fila, fila, "id")
        nombre = _texto_obligatorio(ruta, n_fila, fila, "nombre")
        rol = _texto_obligatorio(ruta, n_fila, fila, "tipo")
        if id_v in vistos:
            raise ErrorCargaCSV(ruta, n_fila, f"id duplicado '{id_v}' (ya aparece en la fila {vistos[id_v]})")
        vistos[id_v] = n_fila
        meta = {}
        for col, valor in fila.items():
            if col in COLUMNAS_VERTICE or valor is None or not valor.strip():
                continue
            if col in ("x_esquema", "y_esquema"):
                meta[col] = float(_numero(ruta, n_fila, valor.strip(), col))
            else:
                meta[col] = valor.strip()
        resultado.append(Vertice(id_v, nombre, rol, meta))
    return resultado


def cargar_aristas(ruta, ids_validos=None):
    """Lee aristas.csv (o grafo_manual.csv) -> lista de Arista.
    Detecta duplicados directos e inversos (N01-N02 y N02-N01).
    """
    mapa, filas = _leer_filas(ruta, ("origen", "destino", "peso_ruta", "peso_red"))
    vistas = {}
    resultado = []
    for n_fila, fila in filas:
        origen = _texto_obligatorio(ruta, n_fila, fila, "origen")
        destino = _texto_obligatorio(ruta, n_fila, fila, "destino")
        if ids_validos is not None:
            for extremo in (origen, destino):
                if extremo not in ids_validos:
                    raise IdDesconocidoCSV(ruta, n_fila, f"id desconocido '{extremo}'")
        if origen == destino:
            raise ErrorCargaCSV(ruta, n_fila, f"lazo no permitido: {origen}-{destino}")
        p_ruta = _peso(ruta, n_fila, _texto_obligatorio(ruta, n_fila, fila, mapa["peso_ruta"]), mapa["peso_ruta"])
        p_red = _peso(ruta, n_fila, _texto_obligatorio(ruta, n_fila, fila, mapa["peso_red"]), mapa["peso_red"])
        clave = tuple(sorted((origen, destino)))
        if clave in vistas:
            raise ErrorCargaCSV(ruta, n_fila,
                                f"arista duplicada o inversa {origen}-{destino} (ya aparece en la fila {vistas[clave]})")
        vistas[clave] = n_fila
        meta = {}
        if "tipo" in fila and fila["tipo"] and fila["tipo"].strip():
            meta["tipo"] = fila["tipo"].strip()   # se conserva si el CSV lo trae
        resultado.append(Arista(origen, destino, p_ruta, p_red, meta))
    return resultado


def cargar_grafo(ruta_vertices, ruta_aristas):
    """Construye el Grafo base a partir de vertices.csv y aristas.csv."""
    vertices = cargar_vertices(ruta_vertices)
    aristas = cargar_aristas(ruta_aristas, {v.id for v in vertices})
    grafo = Grafo()
    for v in vertices:
        grafo.agregar_vertice(v)
    for a in aristas:
        grafo.agregar_arista(a)
    return grafo


def cargar_grafo_base(carpeta="datos"):
    carpeta = Path(carpeta)
    return cargar_grafo(carpeta / "vertices.csv", carpeta / "aristas.csv")


def cargar_grafo_manual(ruta="datos/grafo_manual.csv"):
    """Grafo de 6 vértices (A-F) creado a partir de los extremos de las aristas."""
    aristas = cargar_aristas(ruta)
    ids = sorted({e for a in aristas for e in (a.origen, a.destino)})
    grafo = Grafo()
    for id_v in ids:
        grafo.agregar_vertice(Vertice(id_v, nombre=id_v, rol="manual"))
    for a in aristas:
        grafo.agregar_arista(a)
    return grafo


# exportar
def exportar_grafo_csv(grafo, carpeta, prefijo=""):
    """Guarda vertices y aristas con el mismo formato de entrada (recargable)."""
    if not isinstance(grafo, Grafo):
        raise TypeError("exportar_grafo_csv espera un Grafo")
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_v = carpeta / f"{prefijo}vertices.csv"
    ruta_a = carpeta / f"{prefijo}aristas.csv"
    extra = sorted({k for v in grafo.vertices() for k in v.metadatos})
    with open(ruta_v, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "nombre", "tipo", *extra])
        for v in grafo.vertices():
            meta = v.metadatos
            w.writerow([v.id, v.nombre, v.rol, *[meta.get(k, "") for k in extra]])
    with open(ruta_a, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origen", "destino", "tiempo_entrega_min", "costo_enlace_miles_soles"])
        for a in grafo.aristas():
            w.writerow([a.origen, a.destino, a.peso_ruta, a.peso_red])
    return ruta_v, ruta_a


# generadores
SEMILLA_POR_DEFECTO = 2026
RAZON_DISPERSO = 2        # E = 2V (igual que el grafo base: 48/24)
DENSIDAD_DENSO = 0.25     # E = 25 % de las V(V-1)/2 aristas posibles
CONFIGURACIONES = {
    "100_disperso": (100, "disperso"),
    "100_denso": (100, "denso"),
    "200_disperso": (200, "disperso"),
    "200_denso": (200, "denso"),
}


def aristas_objetivo(n_vertices, tipo):
    """Cantidad de aristas para un grafo 'disperso' o 'denso' de n vértices."""
    if tipo == "disperso":
        return RAZON_DISPERSO * n_vertices
    if tipo == "denso":
        return round(DENSIDAD_DENSO * n_vertices * (n_vertices - 1) / 2)
    raise ValueError("tipo debe ser 'disperso' o 'denso'")


def generar_grafo(n_vertices, n_aristas, semilla=SEMILLA_POR_DEFECTO,
                  rango_ruta=(5, 60), rango_red=(20, 120)):
    """Grafo CONEXO

    1) Árbol aleatorio que garantiza conectividad (V-1 aristas).
    2) Se completan hasta ``n_aristas`` con pares distintos elegidos al azar.
    """
    for nombre, valor in (("n_vertices", n_vertices), ("n_aristas", n_aristas)):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(f"{nombre} debe ser entero")
    if n_vertices < 2:
        raise ValueError("se necesitan al menos 2 vértices")
    maximo = n_vertices * (n_vertices - 1) // 2
    if not (n_vertices - 1 <= n_aristas <= maximo):
        raise ValueError(f"n_aristas debe estar entre {n_vertices - 1} y {maximo}")
    for rango in (rango_ruta, rango_red):
        if rango[0] <= 0 or rango[0] > rango[1]:
            raise ValueError("los rangos de pesos deben ser positivos y ordenados")

    rng = random.Random(semilla)
    ancho = max(2, len(str(n_vertices)))
    ids = [f"N{i:0{ancho}d}" for i in range(1, n_vertices + 1)]
    grafo = Grafo()
    for id_v in ids:
        grafo.agregar_vertice(Vertice(id_v, f"Nodo {id_v}", "sintético"))

    def nueva(a, b):
        return Arista(a, b, rng.randint(*rango_ruta), rng.randint(*rango_red))

    orden = ids[:]
    rng.shuffle(orden)
    for i in range(1, n_vertices):
        grafo.agregar_arista(nueva(orden[i], orden[rng.randrange(i)]))

    faltan = n_aristas - (n_vertices - 1)
    if faltan:
        candidatos = [(ids[i], ids[j]) for i in range(n_vertices)
                      for j in range(i + 1, n_vertices)
                      if not grafo.tiene_arista(ids[i], ids[j])]
        for a, b in rng.sample(candidatos, faltan):
            grafo.agregar_arista(nueva(a, b))
    return grafo


def generar_configuracion(nombre, semilla=SEMILLA_POR_DEFECTO):
    """Una de: 100_disperso, 100_denso, 200_disperso, 200_denso."""
    if nombre not in CONFIGURACIONES:
        raise KeyError(f"configuración desconocida '{nombre}'; opciones: {list(CONFIGURACIONES)}")
    n, tipo = CONFIGURACIONES[nombre]
    return generar_grafo(n, aristas_objetivo(n, tipo), semilla)
