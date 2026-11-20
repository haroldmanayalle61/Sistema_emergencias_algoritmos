"""Caminos mínimos entre todos los vértices con Floyd-Warshall."""

import math

from modelo import Grafo, PESO_RUTA


class FloydWarshall:
    """Calcula distancias mínimas y permite reconstruir caminos."""

    def __init__(self, grafo: Grafo, *, registrar_traza: bool = False):
        if not isinstance(grafo, Grafo):
            raise TypeError("FloydWarshall espera un objeto Grafo")

        if not isinstance(registrar_traza, bool):
            raise TypeError("registrar_traza debe ser bool")

        self.grafo = grafo
        self.registrar_traza = registrar_traza

        # Relación entre los identificadores y las posiciones de las matrices.
        self.ids = []
        self.indice = {}

        self.matriz_distancias = []
        self.matriz_siguiente = []

        self.traza = []
        self.calculado = False

    def _guardar_paso(self, intermedio):
        """Guarda copias de las matrices para explicar el algoritmo."""
        self.traza.append({
            "intermedio": intermedio,
            "matriz_distancias": [
                fila[:] for fila in self.matriz_distancias
            ],
            "matriz_siguiente": [
                fila[:] for fila in self.matriz_siguiente
            ],
        })

    def calcular_todos(self):  # sourcery skip: use-itertools-product
        """Devuelve (matriz_distancias, matriz_siguiente)."""
        self.calculado = False
        self.traza = []

        # Obtener una matriz nueva con los tiempos de entrega.
        matriz, ids = self.grafo.a_matriz_adyacencia(PESO_RUTA)

        self.ids = ids
        self.matriz_distancias = matriz
        self.indice = {}

        for posicion, id_vertice in enumerate(self.ids):
            self.indice[id_vertice] = posicion

        cantidad = len(self.ids)

        # Al principio no conocemos ningún siguiente vértice.
        self.matriz_siguiente = [
            [None] * cantidad for _ in range(cantidad)
        ]

        # Si existe conexión directa, el siguiente paso es el destino.
        # En la diagonal, el siguiente es el propio vértice.
        for i in range(cantidad):
            for j in range(cantidad):
                if self.matriz_distancias[i][j] != math.inf:
                    self.matriz_siguiente[i][j] = self.ids[j]

        if self.registrar_traza:
            self._guardar_paso(None)

        for k in range(cantidad):
            for i in range(cantidad):
                for j in range(cantidad):
                    distancia_actual = self.matriz_distancias[i][j]

                    distancia_por_k = (
                        self.matriz_distancias[i][k]
                        + self.matriz_distancias[k][j]
                    )

                    # Si pasar por k mejora el camino, actualizamos.
                    if distancia_por_k < distancia_actual:
                        self.matriz_distancias[i][j] = distancia_por_k

                        # El primer paso hacia j será el primer paso hacia k.
                        self.matriz_siguiente[i][j] = (
                            self.matriz_siguiente[i][k]
                        )

            if self.registrar_traza:
                self._guardar_paso(self.ids[k])

        self.calculado = True

        return self.matriz_distancias, self.matriz_siguiente

    def reconstruir_camino(self, origen: str, destino: str):
        """Devuelve una lista de ids o None si no existe camino."""
        if not self.calculado:
            raise ValueError("Se debe llamar a calcular_todos primero.")

        if not isinstance(origen, str) or not isinstance(destino, str):
            raise TypeError("El origen y el destino deben ser texto.")

        if origen not in self.indice:
            raise KeyError(f"El origen {origen} no existe en el cálculo.")

        if destino not in self.indice:
            raise KeyError(f"El destino {destino} no existe en el cálculo.")

        i = self.indice[origen]
        j = self.indice[destino]

        if self.matriz_siguiente[i][j] is None:
            return None

        camino = [origen]
        actual = origen

        while actual != destino:
            posicion_actual = self.indice[actual]
            actual = self.matriz_siguiente[posicion_actual][j]
            camino.append(actual)

        return camino