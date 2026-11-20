"""Árbol de expansión mínima mediante el algoritmo de Prim."""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import count

from modelo import Arista, Grafo, PESO_RED


DetalleArista = tuple[str, str, float]
_Candidato = tuple[float, str, str, int, str, Arista]


@dataclass(frozen=True)
class PasoPrim:
    """Resumen opcional de una selección de Prim para traza o explicación."""

    componente: int
    frontera: tuple[DetalleArista, ...]
    aristas_descartadas: tuple[DetalleArista, ...]
    arista_elegida: DetalleArista | None
    vertice_agregado: str | None
    costo_acumulado: float


class Prim:
    """Calcula un árbol mínimo o un bosque si el grafo no es conexo.
    """

    def __init__(self, grafo: Grafo, *, registrar_traza: bool = False) -> None:
        if not isinstance(grafo, Grafo):
            raise TypeError("Prim espera un objeto Grafo")
        if not isinstance(registrar_traza, bool):
            raise TypeError("registrar_traza debe ser bool")

        self.grafo: Grafo = grafo
        self.aristas_seleccionadas: list[Arista] = []
        self.costo_total: float = 0.0
        self.vertices_visitados: set[str] = set()
        self.componentes: list[list[str]] = []
        self.inicio_actual: str | None = None
        self.registrar_traza: bool = registrar_traza
        self.traza: list[PasoPrim] = []

    @property
    def es_bosque(self) -> bool:
        """Indica si el resultado tiene más de un componente conexo."""
        return len(self.componentes) > 1

    @property
    def cobertura(self) -> int:
        """Cantidad de vértices incluidos en el resultado actual."""
        return len(self.vertices_visitados)

    @staticmethod
    def _detalle(arista: Arista, peso: float) -> DetalleArista:
        extremo_a, extremo_b = arista.clave
        return extremo_a, extremo_b, peso

    def _agregar_candidatas(self,id_vertice: str,frontera: list[_Candidato],secuencia: count,) -> None:
        for vecino, arista in self.grafo.vecinos(id_vertice):
            if vecino in self.vertices_visitados:
                continue

            peso = float(arista.peso(PESO_RED))
            extremo_a, extremo_b = arista.clave
            heapq.heappush(frontera,(peso, extremo_a, extremo_b, next(secuencia), vecino, arista),)

    def _frontera_vigente(self, frontera: list[_Candidato]) -> tuple[DetalleArista, ...]:
        candidatas = [
            self._detalle(arista, peso)
            for peso, _, _, _, vecino, arista in frontera
            if vecino not in self.vertices_visitados
        ]
        return tuple(sorted(candidatas, key=lambda item: (item[2], item[0], item[1])))

    def calcular_arbol(self, inicio: str) -> tuple[list[Arista], float]:
        """Calcula desde ``inicio`` y cubre todos los componentes del grafo.
        """
        if inicio not in self.grafo:
            raise KeyError(f"El vértice inicial {inicio} no existe en el grafo.")

        self.aristas_seleccionadas = []
        self.costo_total = 0.0
        self.vertices_visitados = set()
        self.componentes = []
        self.inicio_actual = inicio
        self.traza = []

        raices = [inicio, *(id_vertice for id_vertice in self.grafo.ids() if id_vertice != inicio)]
        secuencia = count()

        for raiz in raices:
            if raiz in self.vertices_visitados:
                continue

            componente: list[str] = []
            self.componentes.append(componente)
            self.vertices_visitados.add(raiz)
            componente.append(raiz)

            frontera: list[_Candidato] = []
            self._agregar_candidatas(raiz, frontera, secuencia)
            if self.registrar_traza:
                self.traza.append(
                    PasoPrim(
                        componente=len(self.componentes),
                        frontera=self._frontera_vigente(frontera),
                        aristas_descartadas=(),
                        arista_elegida=None,
                        vertice_agregado=raiz,
                        costo_acumulado=self.costo_total,
                    )
                )

            while frontera:
                descartadas: list[DetalleArista] = []
                while frontera and frontera[0][4] in self.vertices_visitados:
                    peso_descartado, _, _, _, _, arista_descartada = heapq.heappop(frontera)
                    if self.registrar_traza:
                        descartadas.append(self._detalle(arista_descartada, peso_descartado))

                if not frontera:
                    if self.registrar_traza and descartadas:
                        self.traza.append(
                            PasoPrim(
                                componente=len(self.componentes),
                                frontera=(),
                                aristas_descartadas=tuple(descartadas),
                                arista_elegida=None,
                                vertice_agregado=None,
                                costo_acumulado=self.costo_total,
                            )
                        )
                    break

                if self.registrar_traza:
                    frontera_antes_de_elegir = self._frontera_vigente(frontera)
                peso, _, _, _, vecino, arista = heapq.heappop(frontera)

                # una vez aquí, la arista necesariamente incorpora un vértice.
                self.vertices_visitados.add(vecino)
                componente.append(vecino)
                self.aristas_seleccionadas.append(arista)
                self.costo_total += peso
                self._agregar_candidatas(vecino, frontera, secuencia)

                if self.registrar_traza:
                    self.traza.append(
                        PasoPrim(
                            componente=len(self.componentes),
                            frontera=frontera_antes_de_elegir,
                            aristas_descartadas=tuple(descartadas),
                            arista_elegida=self._detalle(arista, peso),
                            vertice_agregado=vecino,
                            costo_acumulado=self.costo_total,
                        )
                    )

        return self.aristas_seleccionadas, self.costo_total
