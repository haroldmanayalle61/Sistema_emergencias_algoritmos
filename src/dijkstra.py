import heapq
import math
from modelo import Grafo, PESO_RUTA

class Dijkstra:
    def __init__(self, grafo: Grafo, *, registrar_traza: bool = False):
        if not isinstance(registrar_traza, bool):
            raise TypeError("registrar_traza debe ser bool")
        self.grafo = grafo
        self.distancias = {}
        self.predecesores = {}
        self.origen_actual = None
        self.registrar_traza = registrar_traza
        self.traza = []

    def calcular_desde(self, origen: str) :
     
        if origen not in self.grafo:
            raise KeyError(f"El origen {origen} no existe en el grafo.")

        self.origen_actual = origen
        self.distancias = {}
        self.predecesores = {}
        self.traza = []

        for v in self.grafo.ids():
            self.distancias[v] = math.inf
            self.predecesores[v] = None

        self.distancias[origen] = 0
        cola = [(0, origen)]
        visitados = set() 

        while cola:
            distancia_actual, actual = heapq.heappop(cola)

            if self.registrar_traza:
                self.traza.append({
                    "evento": "extraccion",
                    "vertice": actual,
                    "distancia": distancia_actual,
                    "descartada": actual in visitados,
                    "distancias": dict(self.distancias),
                    "predecesores": dict(self.predecesores),
                })

            if actual in visitados:
                continue

            visitados.add(actual)
            for vecino, arista in self.grafo.vecinos(actual):
                if vecino in visitados:
                    continue

                peso_tramo = arista.peso(PESO_RUTA)
                nueva_distancia = distancia_actual + peso_tramo

                if nueva_distancia < self.distancias[vecino]:
                    if self.registrar_traza:
                        self.traza.append({
                            "evento": "relajacion",
                            "origen": actual,
                            "destino": vecino,
                            "distancia_anterior": self.distancias[vecino],
                            "distancia_nueva": nueva_distancia,
                        })
                    self.distancias[vecino] = nueva_distancia
                    self.predecesores[vecino] = actual
                    heapq.heappush(cola, (nueva_distancia, vecino))

        return self.distancias, self.predecesores

    def reconstruir_camino(self, destino: str):
        if not self.origen_actual:
            raise ValueError("Se debe llamar a calcular_desde primero.")
        if destino not in self.grafo:
            raise KeyError(f"El destino {destino} no existe en el grafo.")

        if self.distancias[destino] == math.inf:
            return None

        if self.origen_actual == destino:
            return [destino]

        ruta = []
        actual = destino

        while actual is not None:
            ruta.append(actual)
            actual = self.predecesores[actual]

        ruta.reverse()
        return ruta
