
import cv2
from pathlib import Path

# Carpeta donde se guardarán los marcadores
carpeta = Path("assets") / "tarjetas"
carpeta.mkdir(parents=True, exist_ok=True)

diccionario = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

objetos = {
    1: "llave",
    2: "tarjeta"
}

for identificador, nombre in objetos.items():
    marcador = cv2.aruco.generateImageMarker(
        diccionario, identificador, 400
    )

    ruta = carpeta / f"{nombre}.png"
    cv2.imwrite(str(ruta), marcador)

    print(f"Marcador generado: {ruta}")

print("¡Tarjetas generadas correctamente!")
