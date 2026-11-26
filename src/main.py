"""Menú principal del Sistema de Emergencias."""

from modelo import PESO_RED, PESO_RUTA
from sistema_emergencias import SistemaEmergencias

MENU = """
=== Sistema de Emergencias · Grupo 07 ===
 1. Resumen del grafo base
 2. Ruta mínima entre dos nodos (Dijkstra)
 3. Rutas requeridas (N02 y N03 → N06, N10, N14, N20)
 4. Albergues más alejados de N02
 5. Floyd-Warshall: consulta de camino
 6. Floyd-Warshall: matriz de distancias
 7. Árbol mínimo con Prim
 8. Árbol mínimo con Kruskal y comparación con Prim
 9. Trazas manuales del caso A-F
10. Vulnerabilidad del árbol mínimo (falla de una arista)
11. Escenario de desastre (N02-N08 y N15-N21)
12. Exportar escenario (CSV + tabla antes/después)
13. Demo: modificar el peso de un enlace
14. Prueba de desconexión (aislar un vértice)
 0. Salir
"""


def _pedir(texto, defecto=None):
    sufijo = f" [{defecto}]" if defecto is not None else ""
    valor = input(f"{texto}{sufijo}: ").strip()
    return valor or defecto


def _pedir_id(texto, defecto=None):
    valor = _pedir(texto, defecto)
    return valor.upper() if valor else valor


def _pedir_numero(texto):
    valor = input(f"{texto}: ").strip()
    try:
        return int(valor)
    except ValueError:
        return float(valor)


def _pedir_metrica():
    metrica = _pedir("Métrica (ruta = tiempo en min / red = costo en miles de soles)", "ruta").lower()
    if metrica not in ("ruta", "red"):
        raise ValueError("escriba 'ruta' o 'red'")
    return PESO_RUTA if metrica == "ruta" else PESO_RED


def _resumen(s):
    print(s.texto_resumen())


def _ruta(s):
    origen = _pedir_id("Origen", "N02")
    destino = _pedir_id("Destino", "N20")
    camino, tiempo = s.ruta_minima(origen, destino)
    if camino is None:
        print(f"No existe camino de {origen} a {destino}.")
    else:
        print(f"{' → '.join(camino)}\nTiempo mínimo: {tiempo:g} min")


def _rutas(s):
    print(s.texto_rutas_requeridas())


def _albergues(s):
    print(s.texto_albergues_mas_alejados("N02"))


def _floyd_camino(s):
    origen = _pedir_id("Origen", "N02")
    destino = _pedir_id("Destino", "N20")
    camino, tiempo = s.camino_floyd(origen, destino)
    if camino is None:
        print(f"No existe camino de {origen} a {destino}.")
    else:
        print(f"{' → '.join(camino)}\nTiempo mínimo: {tiempo:g} min")


def _floyd_matriz(s):
    print(s.texto_matriz_floyd())


def _prim(s):
    inicio = _pedir_id("Vértice inicial", "N02")
    print(s.texto_arbol(s.arbol_prim(inicio)))


def _kruskal(s):
    print(s.texto_comparacion_arboles())


def _trazas(s):
    algoritmo = _pedir("Algoritmo (dijkstra/floyd/prim/kruskal/todos)", "todos")
    print(s.texto_trazas_manuales(algoritmo))


def _vulnerabilidad(s):
    texto = _pedir("Arista del MST a retirar (ej. N01-N02) o Enter para la más crítica según tamaño de grupos")
    conexion = tuple(i.strip() for i in texto.upper().split("-")) if texto else None
    if conexion is not None and (len(conexion) != 2 or not all(conexion)):
        raise ValueError("use el formato N01-N02")
    print(s.texto_vulnerabilidad(conexion))
    if _pedir("¿Ver tabla de todas las aristas del MST? (s/n)", "n").lower() == "s":
        print(s.texto_tabla_vulnerabilidad())


def _escenario(s):
    s.ejecutar_escenario()
    print(s.texto_escenario())


def _exportar(s):
    if s.resultado_escenario is None:
        s.ejecutar_escenario()
    for nombre, ruta in s.exportar_escenario().items():
        print(f"{nombre}: {ruta}")


def _demo(s):
    a = _pedir_id("Extremo 1", "N02")
    b = _pedir_id("Extremo 2", "N03")
    metrica = _pedir_metrica()
    valor = _pedir_numero("Nuevo valor (positivo)")
    r = s.demo_modificar_peso(a, b, metrica, valor)
    print(f"Enlace {a}-{b}: {metrica} → {valor:g} (en una copia; la base sigue intacta)\n")
    print(s.texto_tabla(r))
    print(s.texto_rutas(r))
    print(s.texto_pares(r))
    print(s.texto_interpretacion(r))


def _desconexion(s):
    print(s.texto_desconexion(_pedir_id("Vértice a aislar", "N12")))


ACCIONES = {
    "1": _resumen, "2": _ruta, "3": _rutas, "4": _albergues, "5": _floyd_camino,
    "6": _floyd_matriz, "7": _prim, "8": _kruskal, "9": _trazas, "10": _vulnerabilidad,
    "11": _escenario, "12": _exportar, "13": _demo, "14": _desconexion,
}


def main():
    try:
        sistema = SistemaEmergencias()
    except (OSError, KeyError, ValueError, TypeError) as error:
        mensaje = error.args[0] if isinstance(error, KeyError) and error.args else error
        print(f"No se pudo cargar los datos: {mensaje}")
        return 1

    while True:
        print(MENU)
        try:
            opcion = input("Opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if opcion == "0":
            break
        accion = ACCIONES.get(opcion)
        if accion is None:
            print("Opción no válida.")
            continue
        try:
            print()
            accion(sistema)
        except (KeyError, ValueError, TypeError, OSError) as error:
            mensaje = error.args[0] if isinstance(error, KeyError) and error.args else error
            print(f"Error: {mensaje}")
        except (EOFError, KeyboardInterrupt):
            print()
            break
    print("Hasta luego.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())