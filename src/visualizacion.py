"""Dibujo de la red, caminos, árboles de Prim y escenarios.

NetworkX se utiliza solamente para dibujar. La selección de caminos y árboles
se obtiene de las implementaciones propias del proyecto.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from modelo import Arista, Grafo, PESO_RED, PESO_RUTA
from prim import DetalleArista, PasoPrim, Prim


_NOMBRES_METRICA: dict[str, str] = {
    PESO_RUTA: "tiempo_entrega_min",
    PESO_RED: "costo_enlace_miles_soles",
}
_UNIDADES: dict[str, str] = {
    PESO_RUTA: "minutos de entrega estimado",
    PESO_RED: "miles de soles de enlace de emergencia",
}
_ARISTA_RESALTADA = "#17803d"
_RUTA_COLOR = "#d64a3b"
_ARISTA_RETIRADA = "#b52b38"
_ARISTA_NORMAL = "#b6c0c9"


def _importar_librerias_dibujo():
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        from matplotlib.lines import Line2D
    except ImportError as error:
        raise RuntimeError(
            "Las figuras requieren matplotlib y networkx. Instálelos para "
            "ejecutar las funciones de visualización."
        ) from error
    return plt, nx, Line2D


def _crear_grafo_visual(grafo: Grafo, nx):
    red = nx.Graph()
    red.add_nodes_from(grafo.ids())
    for arista in grafo.aristas():
        red.add_edge(arista.origen, arista.destino)
    return red


def _obtener_posiciones(
    grafo: Grafo,
    red,
    nx,
    posiciones: Mapping[str, tuple[float, float]] | None = None,
) -> dict[str, tuple[float, float]]:
    ids = grafo.ids()
    if posiciones is not None:
        faltantes = set(ids) - set(posiciones)
        if faltantes:
            raise ValueError(f"faltan coordenadas para: {sorted(faltantes)}")
        return {
            id_vertice: (float(posiciones[id_vertice][0]), float(posiciones[id_vertice][1]))
            for id_vertice in ids
        }

    coordenadas: dict[str, tuple[float, float]] = {}
    for vertice in grafo.vertices():
        metadatos = vertice.metadatos
        try:
            x = float(metadatos["x_esquema"])
            y = float(metadatos["y_esquema"])
        except (KeyError, TypeError, ValueError):
            coordenadas = {}
            break
        if not (math.isfinite(x) and math.isfinite(y)):
            coordenadas = {}
            break
        coordenadas[vertice.id] = (x, y)

    if len(coordenadas) == len(ids):
        return coordenadas
    if not ids:
        return {}
    return nx.spring_layout(red, seed=2026, weight=None)


def _validar_metrica(metrica: str) -> None:
    if metrica not in _NOMBRES_METRICA:
        raise ValueError("metrica debe ser 'peso_ruta' o 'peso_red'")


def _claves_ruta(grafo: Grafo, ruta: Sequence[str] | None) -> set[tuple[str, str]]:
    if ruta is None:
        return set()
    for id_vertice in ruta:
        if id_vertice not in grafo:
            raise KeyError(f"la ruta incluye el vértice desconocido {id_vertice}")
    claves: set[tuple[str, str]] = set()
    for origen, destino in zip(ruta, ruta[1:]):
        if not grafo.tiene_arista(origen, destino):
            raise ValueError(f"la ruta no es continua: no existe {origen}-{destino}")
        claves.add(tuple(sorted((origen, destino))))
    return claves


def _normalizar_fallos(
    grafo: Grafo,
    conexiones_fallidas: Iterable[tuple[str, str]],
) -> set[tuple[str, str]]:
    claves: set[tuple[str, str]] = set()
    for origen, destino in conexiones_fallidas:
        if not grafo.tiene_arista(origen, destino):
            raise ValueError(f"la conexión marcada como retirada no existe: {origen}-{destino}")
        claves.add(tuple(sorted((origen, destino))))
    return claves


def _dibujar_en_eje(
    ax,
    nx,
    line2d,
    grafo: Grafo,
    *,
    metrica: str,
    titulo: str,
    aristas_resaltadas: Iterable[Arista] = (),
    ruta: Sequence[str] | None = None,
    conexiones_fallidas: Iterable[tuple[str, str]] = (),
    posiciones: Mapping[str, tuple[float, float]] | None = None,
    mostrar_pesos: bool = True,
) -> dict[str, tuple[float, float]]:
    _validar_metrica(metrica)
    red = _crear_grafo_visual(grafo, nx)
    pos = _obtener_posiciones(grafo, red, nx, posiciones)

    claves_resaltadas = {arista.clave for arista in aristas_resaltadas}
    claves_ruta = _claves_ruta(grafo, ruta)
    claves_fallidas = _normalizar_fallos(grafo, conexiones_fallidas)
    claves_existentes = {arista.clave for arista in grafo.aristas()}
    desconocidas = (claves_resaltadas | claves_ruta | claves_fallidas) - claves_existentes
    if desconocidas:
        raise ValueError(f"hay aristas resaltadas que no pertenecen al grafo: {sorted(desconocidas)}")

    aristas_normales: list[tuple[str, str]] = []
    aristas_del_arbol: list[tuple[str, str]] = []
    aristas_de_ruta: list[tuple[str, str]] = []
    aristas_retiradas: list[tuple[str, str]] = []
    for arista in grafo.aristas():
        clave = arista.clave
        extremos = (arista.origen, arista.destino)
        if clave in claves_fallidas:
            aristas_retiradas.append(extremos)
        elif clave in claves_ruta:
            aristas_de_ruta.append(extremos)
        elif clave in claves_resaltadas:
            aristas_del_arbol.append(extremos)
        else:
            aristas_normales.append(extremos)

    nx.draw_networkx_edges(
        red, pos, edgelist=aristas_normales, ax=ax, edge_color=_ARISTA_NORMAL, width=1.2, alpha=0.85
    )
    nx.draw_networkx_edges(
        red, pos, edgelist=aristas_del_arbol, ax=ax, edge_color=_ARISTA_RESALTADA, width=2.8
    )
    nx.draw_networkx_edges(
        red, pos, edgelist=aristas_de_ruta, ax=ax, edge_color=_RUTA_COLOR, width=3.2
    )
    nx.draw_networkx_edges(
        red,
        pos,
        edgelist=aristas_retiradas,
        ax=ax,
        edge_color=_ARISTA_RETIRADA,
        width=2.8,
        style="dashed",
    )
    nx.draw_networkx_nodes(
        red,
        pos,
        ax=ax,
        node_size=850 if grafo.num_vertices <= 30 else 500,
        node_color="#e8f1f8",
        edgecolors="#284b63",
        linewidths=1.2,
    )
    nx.draw_networkx_labels(red, pos, ax=ax, font_size=8, font_weight="bold", font_color="#183247")

    if mostrar_pesos:
        etiquetas = {
            (arista.origen, arista.destino): f"{arista.peso(metrica):g}"
            for arista in grafo.aristas()
        }
        nx.draw_networkx_edge_labels(
            red, pos, edge_labels=etiquetas, ax=ax, font_size=7, rotate=False, label_pos=0.52
        )

    ax.set_title(
        f"{titulo}\nMétrica: {_NOMBRES_METRICA[metrica]} ({_UNIDADES[metrica]})",
        fontsize=11,
    )
    ax.axis("off")
    ax.margins(0.18)

    leyenda = []
    if aristas_del_arbol:
        leyenda.append(line2d([0], [0], color=_ARISTA_RESALTADA, lw=3, label="Aristas del árbol de Prim"))
    if aristas_de_ruta:
        leyenda.append(line2d([0], [0], color=_RUTA_COLOR, lw=3, label="Camino mínimo resaltado"))
    if aristas_retiradas:
        leyenda.append(
            line2d([0], [0], color=_ARISTA_RETIRADA, lw=2.5, ls="--", label="Conexión retirada en el escenario")
        )
    if leyenda:
        ax.legend(handles=leyenda, loc="best", fontsize=8, framealpha=0.92)
    return dict(pos)


def dibujar_grafo(
    grafo: Grafo,
    archivo: str | Path,
    *,
    metrica: str,
    titulo: str,
    aristas_resaltadas: Iterable[Arista] = (),
    ruta: Sequence[str] | None = None,
    conexiones_fallidas: Iterable[tuple[str, str]] = (),
    posiciones: Mapping[str, tuple[float, float]] | None = None,
    mostrar_pesos: bool = True,
    mostrar: bool = False,
) -> Path:
    """Dibuja la red y guarda una figura PNG con métrica y unidades explícitas."""
    plt, nx, line2d = _importar_librerias_dibujo()
    _validar_metrica(metrica)
    destino = Path(archivo)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(15, 11))
    _dibujar_en_eje(
        ax,
        nx,
        line2d,
        grafo,
        metrica=metrica,
        titulo=titulo,
        aristas_resaltadas=aristas_resaltadas,
        ruta=ruta,
        conexiones_fallidas=conexiones_fallidas,
        posiciones=posiciones,
        mostrar_pesos=mostrar_pesos,
    )
    fig.tight_layout()
    fig.savefig(destino, dpi=180, bbox_inches="tight")
    if mostrar:
        plt.show()
    plt.close(fig)
    return destino


def dibujar_antes_despues(
    grafo_antes: Grafo,
    grafo_despues: Grafo,
    archivo: str | Path,
    *,
    conexiones_retiradas: Iterable[tuple[str, str]],
    aristas_prim_antes: Iterable[Arista] = (),
    aristas_prim_despues: Iterable[Arista] = (),
    costo_antes: float | None = None,
    costo_despues: float | None = None,
    metrica: str = PESO_RED,
    mostrar: bool = False,
) -> Path:
    """Compara dos copias del mismo conjunto de vértices lado a lado."""
    if set(grafo_antes.ids()) != set(grafo_despues.ids()):
        raise ValueError("la comparación antes/después requiere los mismos vértices")
    plt, nx, line2d = _importar_librerias_dibujo()
    _validar_metrica(metrica)
    retiradas = tuple(conexiones_retiradas)
    posiciones = _obtener_posiciones(grafo_antes, _crear_grafo_visual(grafo_antes, nx), nx)
    fig, (ax_antes, ax_despues) = plt.subplots(1, 2, figsize=(22, 10))

    comp_antes = len(grafo_antes.componentes_conexas())
    comp_despues = len(grafo_despues.componentes_conexas())
    tipo_antes = "árbol" if comp_antes <= 1 else "bosque"
    tipo_despues = "árbol" if comp_despues <= 1 else "bosque"
    titulo_antes = (
        f"Antes · cobertura {grafo_antes.num_vertices}/{grafo_antes.num_vertices} · "
        f"{grafo_antes.num_aristas} conexiones · {comp_antes} componente(s), {tipo_antes}"
    )
    titulo_despues = (
        f"Después · cobertura {grafo_despues.num_vertices}/{grafo_despues.num_vertices} · "
        f"{grafo_despues.num_aristas} conexiones · {comp_despues} componente(s), {tipo_despues}"
    )
    if costo_antes is not None:
        titulo_antes += f"\nCosto del árbol: {costo_antes:g}"
    if costo_despues is not None:
        titulo_despues += f"\nCosto del árbol: {costo_despues:g}"

    _dibujar_en_eje(
        ax_antes,
        nx,
        line2d,
        grafo_antes,
        metrica=metrica,
        titulo=titulo_antes,
        aristas_resaltadas=aristas_prim_antes,
        conexiones_fallidas=retiradas,
        posiciones=posiciones,
        mostrar_pesos=True,
    )
    _dibujar_en_eje(
        ax_despues,
        nx,
        line2d,
        grafo_despues,
        metrica=metrica,
        titulo=titulo_despues,
        aristas_resaltadas=aristas_prim_despues,
        posiciones=posiciones,
        mostrar_pesos=True,
    )
    fig.suptitle("Red de comunicaciones antes y después del cierre de corredores", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    destino = Path(archivo)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=180, bbox_inches="tight")
    if mostrar:
        plt.show()
    plt.close(fig)
    return destino


def _formatear_aristas(aristas: Iterable[DetalleArista]) -> str:
    return ", ".join(f"{a}–{b} ({peso:g})" for a, b, peso in aristas) or "ninguna"


def formatear_traza_prim(traza: Sequence[PasoPrim]) -> str:
    """Convierte la traza opcional a texto para el caso manual A-F."""
    lineas: list[str] = []
    for numero, paso in enumerate(traza, start=1):
        lineas.append(f"Paso {numero} · componente {paso.componente}")
        lineas.append(f"  Frontera: {_formatear_aristas(paso.frontera)}")
        if paso.aristas_descartadas:
            lineas.append(
                "  Descartadas por cerrar un ciclo: "
                f"{_formatear_aristas(paso.aristas_descartadas)}"
            )
        if paso.arista_elegida is not None:
            lineas.append(f"  Arista elegida: {_formatear_aristas((paso.arista_elegida,))}")
        if paso.vertice_agregado is not None:
            lineas.append(f"  Vértice incorporado: {paso.vertice_agregado}")
        lineas.append(f"  Costo acumulado: {paso.costo_acumulado:g} miles de soles")
    return "\n".join(lineas)


def generar_figuras_resultados(
    carpeta_salida: str | Path | None = None,
) -> dict[str, Path]:
    """Genera las figuras del grafo base, rutas, árboles y escenario obligatorio.

    Se ejecuta manualmente con ``python src/visualizacion.py``. El cronómetro
    de experimentos no incluye estas llamadas de dibujo.
    """
    from datos import cargar_grafo_base
    from dijkstra import Dijkstra

    raiz_proyecto = Path(__file__).resolve().parents[1]
    salida = Path(carpeta_salida) if carpeta_salida is not None else raiz_proyecto / "resultados" / "figuras"
    salida.mkdir(parents=True, exist_ok=True)
    grafo_base = cargar_grafo_base(raiz_proyecto / "datos")
    figuras: dict[str, Path] = {}

    figuras["red_inicial"] = dibujar_grafo(
        grafo_base,
        salida / "red_inicial.png",
        metrica=PESO_RED,
        titulo=f"Red inicial · {grafo_base.num_vertices} vértices y {grafo_base.num_aristas} corredores",
        mostrar_pesos=True,
    )

    destinos = ("N06", "N10", "N14", "N20")
    for origen in ("N02", "N03"):
        dijkstra = Dijkstra(grafo_base)
        distancias, _ = dijkstra.calcular_desde(origen)
        for destino in destinos:
            camino = dijkstra.reconstruir_camino(destino)
            costo = distancias[destino]
            titulo = (
                f"Camino mínimo {origen} → {destino} · {costo:g} min"
                if camino is not None
                else f"Camino mínimo {origen} → {destino} · inalcanzable"
            )
            nombre = f"ruta_{origen}_{destino}"
            figuras[nombre] = dibujar_grafo(
                grafo_base,
                salida / f"{nombre}.png",
                metrica=PESO_RUTA,
                titulo=titulo,
                ruta=camino,
                mostrar_pesos=True,
            )

    prim_n02 = Prim(grafo_base)
    aristas_n02, costo_n02 = prim_n02.calcular_arbol("N02")
    figuras["mst_n02"] = dibujar_grafo(
        grafo_base,
        salida / "mst_n02.png",
        metrica=PESO_RED,
        titulo=(
            f"Prim desde N02 · cobertura {prim_n02.cobertura}/{grafo_base.num_vertices} · "
            f"{len(aristas_n02)} aristas · costo {costo_n02:g}"
        ),
        aristas_resaltadas=aristas_n02,
    )

    prim_n03 = Prim(grafo_base)
    aristas_n03, costo_n03 = prim_n03.calcular_arbol("N03")
    figuras["mst_n03"] = dibujar_grafo(
        grafo_base,
        salida / "mst_n03.png",
        metrica=PESO_RED,
        titulo=(
            f"Prim desde N03 · cobertura {prim_n03.cobertura}/{grafo_base.num_vertices} · "
            f"{len(aristas_n03)} aristas · costo {costo_n03:g}"
        ),
        aristas_resaltadas=aristas_n03,
    )

    conexiones_retiradas = (("N02", "N08"), ("N15", "N21"))
    escenario = grafo_base.copiar()
    for origen, destino in conexiones_retiradas:
        escenario.eliminar_arista(origen, destino)
    prim_escenario = Prim(escenario)
    aristas_escenario, costo_escenario = prim_escenario.calcular_arbol("N02")
    figuras["antes_despues"] = dibujar_antes_despues(
        grafo_base,
        escenario,
        salida / "mst_antes_despues.png",
        conexiones_retiradas=conexiones_retiradas,
        aristas_prim_antes=aristas_n02,
        aristas_prim_despues=aristas_escenario,
        costo_antes=costo_n02,
        costo_despues=costo_escenario,
        metrica=PESO_RED,
    )

    return figuras


if __name__ == "__main__":
    for nombre, archivo in generar_figuras_resultados().items():
        print(f"{nombre}: {archivo}")
