import math

PESO_RUTA = "peso_ruta"
PESO_RED = "peso_red"
METRICAS = (PESO_RUTA, PESO_RED)


def _validar_metrica(metrica):
    if not isinstance(metrica, str):
        raise TypeError("la métrica debe ser un texto: 'peso_ruta' o 'peso_red'")
    if metrica not in METRICAS:
        raise ValueError(f"métrica desconocida '{metrica}'; use 'peso_ruta' o 'peso_red'")
    return metrica


def _validar_peso(valor, nombre):
    """Un peso válido es numérico, finito y estrictamente positivo."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nombre} debe ser numérico, se recibió {type(valor).__name__}")
    if not math.isfinite(valor) or valor <= 0:
        raise ValueError(f"{nombre} debe ser positivo y finito, se recibió {valor}")
    return valor


class Vertice:
    """Instalación de la red. Dos vértices son iguales si tienen el mismo id."""

    def __init__(self, id, nombre="", rol="", metadatos=None):
        if not isinstance(id, str):
            raise TypeError("el id del vértice debe ser texto")
        if not id.strip():
            raise ValueError("el id del vértice no puede estar vacío")
        if metadatos is not None and not isinstance(metadatos, dict):
            raise TypeError("los metadatos deben ser un diccionario")
        self._id = id.strip()
        self._nombre = str(nombre)
        self._rol = str(rol)
        self._metadatos = dict(metadatos) if metadatos else {}

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def rol(self):
        return self._rol

    @property
    def metadatos(self):
        """Copia de los metadatos (coordenadas esquemáticas, etc.)."""
        return dict(self._metadatos)

    def copiar(self):
        return Vertice(self._id, self._nombre, self._rol, self._metadatos)

    def __eq__(self, otro):
        return isinstance(otro, Vertice) and self._id == otro._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"Vertice({self._id!r}, {self._nombre!r}, rol={self._rol!r})"


class Arista:
    """Conexión no dirigida entre dos ids, con ``peso_ruta`` y ``peso_red``."""

    def __init__(self, origen:Vertice, destino:Vertice, peso_ruta, peso_red, metadatos=None):
        if not isinstance(origen, str) or not isinstance(destino, str):
            raise TypeError("origen y destino deben ser ids (texto)")
        if origen == destino:
            raise ValueError(f"no se permiten lazos: {origen}-{destino}")
        if metadatos is not None and not isinstance(metadatos, dict):
            raise TypeError("los metadatos deben ser un diccionario")
        self._origen = origen
        self._destino = destino
        self._peso_ruta = _validar_peso(peso_ruta, "peso_ruta")
        self._peso_red = _validar_peso(peso_red, "peso_red")
        self._metadatos = dict(metadatos) if metadatos else {}

    @property
    def origen(self):
        return self._origen

    @property
    def destino(self):
        return self._destino

    @property
    def peso_ruta(self):
        return self._peso_ruta

    @peso_ruta.setter
    def peso_ruta(self, valor):
        """Permite cambiar el peso en la demo en vivo; sigue validando."""
        self._peso_ruta = _validar_peso(valor, "peso_ruta")

    @property
    def peso_red(self):
        return self._peso_red

    @peso_red.setter
    def peso_red(self, valor):
        self._peso_red = _validar_peso(valor, "peso_red")

    @property
    def metadatos(self):
        return dict(self._metadatos)

    @property
    def clave(self):
        """Identificador sin dirección: N01-N02 y N02-N01 dan la misma clave."""
        return tuple(sorted((self._origen, self._destino)))

    def peso(self, metrica):
        """Devuelve el peso de la métrica pedida ('peso_ruta' o 'peso_red')."""
        _validar_metrica(metrica)
        return self._peso_ruta if metrica == PESO_RUTA else self._peso_red

    def otro_extremo(self, id_vertice):
        if id_vertice == self._origen:
            return self._destino
        if id_vertice == self._destino:
            return self._origen
        raise KeyError(f"{id_vertice} no es extremo de la arista {self._origen}-{self._destino}")

    def copiar(self):
        return Arista(self._origen, self._destino, self._peso_ruta, self._peso_red, self._metadatos)

    def __repr__(self):
        return (f"Arista({self._origen}-{self._destino}, "
                f"ruta={self._peso_ruta} min, red={self._peso_red} miles de soles)")


class Grafo:
    """Grafo no dirigido y ponderado (dos pesos) con adyacencia por diccionarios.

    ``_vertices``: id -> Vertice.  ``_adyacencia``: id -> {id_vecino: Arista}.
    Cada conexión es UN solo objeto Arista referenciado desde sus dos extremos.
    """

    def __init__(self):
        self._vertices = {}
        self._adyacencia = {}

    # ------------------------------------------------------------ consulta
    def _requerir(self, id_vertice):
        if id_vertice not in self._vertices:
            raise KeyError(f"vértice desconocido: {id_vertice}")

    def __contains__(self, id_vertice):
        return id_vertice in self._vertices

    def __len__(self):
        return len(self._vertices)

    @property
    def num_vertices(self):
        return len(self._vertices)

    @property
    def num_aristas(self):
        return sum(len(v) for v in self._adyacencia.values()) // 2

    def vertices(self):
        """Lista de objetos Vertice en orden de inserción."""
        return list(self._vertices.values())

    def ids(self):
        return list(self._vertices)

    def obtener_vertice(self, id_vertice):
        self._requerir(id_vertice)
        return self._vertices[id_vertice]

    def aristas(self):
        """Conexiones únicas (cada no dirigida UNA vez), orden determinista."""
        resultado = []
        for id_v, vecinos in self._adyacencia.items():
            for arista in vecinos.values():
                if arista.origen == id_v:
                    resultado.append(arista)
        return resultado

    def vecinos(self, id_vertice)->list[tuple[Vertice,Arista]]:
        """Lista de pares (id_vecino, Arista)."""
        self._requerir(id_vertice)
        return [(v, a) for v, a in self._adyacencia[id_vertice].items()]

    def grado(self, id_vertice):
        self._requerir(id_vertice)
        return len(self._adyacencia[id_vertice])

    def obtener_arista(self, a, b):
        """Arista entre a y b (en cualquier sentido) o None si no existe."""
        self._requerir(a)
        self._requerir(b)
        return self._adyacencia[a].get(b)

    def tiene_arista(self, a, b):
        return self.obtener_arista(a, b) is not None

    def peso(self, a, b, metrica):
        """Peso de la conexión a-b; ``math.inf`` si no hay conexión directa."""
        _validar_metrica(metrica)
        arista = self.obtener_arista(a, b)
        return math.inf if arista is None else arista.peso(metrica)

    # --------------------------------------------------------- modificación
    def agregar_vertice(self, vertice):
        if not isinstance(vertice, Vertice):
            raise TypeError("agregar_vertice espera un objeto Vertice")
        if vertice.id in self._vertices:
            raise ValueError(f"vértice duplicado: {vertice.id}")
        self._vertices[vertice.id] = vertice
        self._adyacencia[vertice.id] = {}

    def eliminar_vertice(self, id_vertice):
        """Quita el vértice y TODAS sus conexiones."""
        self._requerir(id_vertice)
        for vecino in list(self._adyacencia[id_vertice]):
            del self._adyacencia[vecino][id_vertice]
        del self._adyacencia[id_vertice]
        del self._vertices[id_vertice]

    def agregar_arista(self, arista):
        if not isinstance(arista, Arista):
            raise TypeError("agregar_arista espera un objeto Arista")
        self._requerir(arista.origen)
        self._requerir(arista.destino)
        if arista.destino in self._adyacencia[arista.origen]:
            raise ValueError(f"arista duplicada (o inversa): {arista.origen}-{arista.destino}")
        self._adyacencia[arista.origen][arista.destino] = arista
        self._adyacencia[arista.destino][arista.origen] = arista

    def eliminar_arista(self, a, b):
        """Quita la conexión a-b (en cualquier sentido) y la devuelve."""
        self._requerir(a)
        self._requerir(b)
        if b not in self._adyacencia[a]:
            raise KeyError(f"no existe la arista {a}-{b}")
        arista = self._adyacencia[a].pop(b)
        del self._adyacencia[b][a]
        return arista

    def copiar(self):
        """Copia profunda e independiente: cambiar la copia no toca el original."""
        nuevo = Grafo()
        for v in self._vertices.values():
            nuevo.agregar_vertice(v.copiar())
        for a in self.aristas():
            nuevo.agregar_arista(a.copiar())
        return nuevo

    # conectividad
    def componentes_conexas(self):
        """Lista de componentes; cada una es una lista de ids (BFS iterativo)."""
        visitados = set()
        componentes = []
        for inicio in self._vertices:
            if inicio in visitados:
                continue
            visitados.add(inicio)
            cola = [inicio]
            componente = []
            while cola:
                actual = cola.pop()
                componente.append(actual)
                for vecino in self._adyacencia[actual]:
                    if vecino not in visitados:
                        visitados.add(vecino)
                        cola.append(vecino)
            componentes.append(componente)
        return componentes

    def es_conexo(self):
        """Un grafo vacío o de un vértice se considera conexo."""
        return len(self.componentes_conexas()) <= 1

    # representaciones
    def a_lista_adyacencia(self, metrica):
        """{id: [(id_vecino, peso), ...]} usando solo la métrica indicada."""
        _validar_metrica(metrica)
        return {
            id_v: [(vec, ar.peso(metrica)) for vec, ar in vecinos.items()]
            for id_v, vecinos in self._adyacencia.items()
        }

    def a_matriz_adyacencia(self, metrica):
        """Devuelve (matriz, ids): diagonal 0, sin conexión ``math.inf``, simétrica."""
        _validar_metrica(metrica)
        ids = list(self._vertices)
        indice = {id_v: i for i, id_v in enumerate(ids)}
        n = len(ids)
        matriz = [[math.inf] * n for _ in range(n)]
        for i in range(n):
            matriz[i][i] = 0
        for arista in self.aristas():
            i, j = indice[arista.origen], indice[arista.destino]
            matriz[i][j] = matriz[j][i] = arista.peso(metrica)
        return matriz, ids

    def __repr__(self):
        return f"Grafo({self.num_vertices} vértices, {self.num_aristas} aristas)"