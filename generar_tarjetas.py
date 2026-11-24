
import cv2
from pathlib import Path

# Configuracion de rutas
BASE_DIR = Path(__file__).resolve().parent
CARPETA_TARJETAS = BASE_DIR / "assets" / "tarjetas"

CARPETA_TARJETAS.mkdir(parents=True, exist_ok=True)

# Configuracion ArUco
DICCIONARIO = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

TAMANO_MARCADOR = 600
MARGEN = 100

TARJETAS = {
    2: "acceso.png",
    3: "prueba_incorrecta.png"
}


def generar_tarjeta(id_marcador, nombre_archivo):

    marcador = cv2.aruco.generateImageMarker(
        DICCIONARIO,
        id_marcador,
        TAMANO_MARCADOR
    )

    # Margen blanco necesario para facilitar la deteccion
    tarjeta = cv2.copyMakeBorder(
        marcador,
        MARGEN,
        MARGEN,
        MARGEN,
        MARGEN,
        cv2.BORDER_CONSTANT,
        value=255
    )

    ruta = CARPETA_TARJETAS / nombre_archivo

    if not cv2.imwrite(str(ruta), tarjeta):
        raise IOError(f"No se pudo guardar: {ruta}")

    print(f"Tarjeta generada: {nombre_archivo}")
    print(f"ID: {id_marcador}")
    print(f"Ruta: {ruta}")
    print("-" * 40)


if __name__ == "__main__":

    print("ENIGMA: Ecos del Olvido")
    print("Generador de tarjetas ArUco")
    print("=" * 40)

    for id_marcador, nombre in TARJETAS.items():
        generar_tarjeta(id_marcador, nombre)

    print("Todas las tarjetas fueron generadas.")
