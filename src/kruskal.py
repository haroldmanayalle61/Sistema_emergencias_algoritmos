"""Árbol o bosque de expansión mínima por Kruskal y conjuntos disjuntos."""

from dataclasses import dataclass
from typing import Iterable
from modelo import Arista, Grafo, PESO_RED


class ConjuntosDisjuntos:
    """Agrupa ids con compresión de caminos y unión por rango."""

    def __init__(self, ids: Iterable[str]) -> None:
        self._padre = {id_vertice: id_vertice for id_vertice in ids}
        self._rango = {id_vertice: 0 for id_vertice in self._padre}

    def find(self, id_vertice: str) -> str:
        if id_vertice not in self._padre:
            raise KeyError(f"vértice desconocido: {id_vertice}")

        raiz = id_vertice
        while self._padre[raiz] != raiz:
            raiz = self._padre[raiz]

        # Cada nodo del camino pasa a apuntar directamente al representante.
        while id_vertice != raiz:
            siguiente = self._padre[id_vertice]
            self._padre[id_vertice] = raiz
            id_vertice = siguiente
        return raiz

    def union(self, a: str, b: str) -> bool:
        raiz_a = self.find(a)
        raiz_b = self.find(b)
        if raiz_a == raiz_b:
            return False

        # El árbol de menor rango queda debajo del de mayor rango.
        if self._rango[raiz_a] < self._rango[raiz_b]:
            raiz_a, raiz_b = raiz_b, raiz_a
        self._padre[raiz_b] = raiz_a
        if self._rango[raiz_a] == self._rango[raiz_b]:
            self._rango[raiz_a] += 1
        return True


@dataclass(frozen=True)
class PasoKruskal:
    """Representantes antes de decidir y costo después de procesar la arista."""

    arista: tuple[str, str, float]
    representante_origen: str
    representante_destino: str
    aceptada: bool
    costo_acumulado: float


class Kruskal:
    """Usa peso_red y procesa cada conexión no dirigida una sola vez.

    Ordenamiento O(E log E), más operaciones de Union-Find de costo casi
    constante amortizado. Memoria O(V+E), incluida la lista ordenada.
    """

    def __init__(self, grafo: Grafo, *, registrar_traza: bool = False) -> None:
        if not isinstance(grafo, Grafo):
            raise TypeError("Kruskal espera un objeto Grafo")
        if not isinstance(registrar_traza, bool):
            raise TypeError("registrar_traza debe ser bool")
        self.grafo = grafo
        self.registrar_traza = registrar_traza
        self.aristas_seleccionadas: list[Arista] = []
        self.costo_total: float = 0
        self.componentes: list[list[str]] = []
        self.traza: list[PasoKruskal] = []

    @property
    def es_bosque(self) -> bool:
        return len(self.componentes) > 1

    @property
    def cobertura(self) -> int:
        """Incluye los vértices aislados como componentes individuales."""
        return sum(len(componente) for componente in self.componentes)

    def calcular_arbol(self) -> tuple[list[Arista], float]:
        self.aristas_seleccionadas = []
        self.costo_total = 0
        self.componentes = []
        self.traza = []
        conjuntos = ConjuntosDisjuntos(self.grafo.ids())
        ordenadas = sorted(
            self.grafo.aristas(),
            key=lambda arista: (arista.peso(PESO_RED), arista.clave),
        )

        # Procesar todas permite explicar también los rechazos del caso manual.
        for arista in ordenadas:
            a, b = arista.clave
            if self.registrar_traza:
                representante_origen = conjuntos.find(a)
                representante_destino = conjuntos.find(b)

            aceptada = conjuntos.union(a, b)
            if aceptada:
                self.aristas_seleccionadas.append(arista)
                self.costo_total += arista.peso(PESO_RED)

            if self.registrar_traza:
                self.traza.append(PasoKruskal(
                    arista=(a, b, arista.peso(PESO_RED)),
                    representante_origen=representante_origen,
                    representante_destino=representante_destino,
                    aceptada=aceptada,
                    costo_acumulado=self.costo_total,
                ))

        grupos: dict[str, list[str]] = {}
        for id_vertice in self.grafo.ids():
            representante = conjuntos.find(id_vertice)
            grupos.setdefault(representante, []).append(id_vertice)
        self.componentes = list(grupos.values())
        return self.aristas_seleccionadas, self.costo_total
