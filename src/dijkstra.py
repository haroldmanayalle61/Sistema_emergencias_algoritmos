import heapq
import math

from datos import PESO_RUTA

class Dijkstra:
    def __init__(self, grafo):
        self.grafo = grafo
        self.distancias = {}
        self.predecesores = {}
        self.origen_actual = None

    def calcular_desde(self, origen: str):

        if origen not in self.grafo:
            raise KeyError(f"El origen {origen} no existe en el grafo.")

        self.origen_actual = origen

        for v in self.grafo.ids():
            self.distancias[v] = math.inf
            self.predecesores[v] = None

        self.distancias[origen] = 0
        cola = [(0, origen)]
        visitados = set()

        while cola:
            distancia_actual, actual = heapq.heappop(cola)

            if actual in visitados:
                continue

            visitados.add(actual)
            for vecino, arista in self.grafo.vecinos(actual):
                if vecino in visitados:
                    continue

                peso_tramo = arista.peso(PESO_RUTA)
                nueva_distancia = distancia_actual + peso_tramo

                if nueva_distancia < self.distancias[vecino]:
                    self.distancias[vecino] = nueva_distancia
                    self.predecesores[vecino] = actual
                    heapq.heappush(cola, (nueva_distancia, vecino))

        return self.distancias, self.predecesores

    def reconstruir_camino(self, destino: str):
        """
        Devuelve la lista de ids del camino, o None si el destino es inalcanzable.
        """
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