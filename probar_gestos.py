
import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Cargar modelo
opciones = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(
        model_asset_path="modelos/hand_landmarker.task"
    ),
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(opciones)

# Índices de las puntas de los dedos
PUNTAS = [8, 12, 16, 20]
ARTICULACIONES = [6, 10, 14, 18]


def reconocer_gesto(mano):
    dedos_extendidos = []

    for punta, articulacion in zip(
        PUNTAS, ARTICULACIONES
    ):
        extendido = (
            mano[punta].y < mano[articulacion].y
        )
        dedos_extendidos.append(extendido)

    if all(dedos_extendidos):
        return "MANO ABIERTA"

    if not any(dedos_extendidos):
        return "PUNO CERRADO"

    if dedos_extendidos == [
        True, False, False, False
    ]:
        return "INDICE LEVANTADO"

    return "GESTO NO RECONOCIDO"


camara = cv2.VideoCapture(0)

if not camara.isOpened():
    detector.close()
    raise RuntimeError("No se pudo abrir la camara.")

print("Presiona Q para salir.")

try:
    while True:
        correcto, imagen = camara.read()

        if not correcto:
            break

        imagen = cv2.flip(imagen, 1)

        rgb = cv2.cvtColor(
            imagen,
            cv2.COLOR_BGR2RGB
        )

        imagen_mp = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        resultado = detector.detect(imagen_mp)

        gesto = "SIN MANO DETECTADA"

        if resultado.hand_landmarks:
            mano = resultado.hand_landmarks[0]
            gesto = reconocer_gesto(mano)

            alto, ancho = imagen.shape[:2]

            for punto in mano:
                x = int(punto.x * ancho)
                y = int(punto.y * alto)

                cv2.circle(
                    imagen,
                    (x, y),
                    4,
                    (0, 255, 0),
                    -1
                )

        cv2.putText(
            imagen,
            gesto,
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "ENIGMA - Reconocimiento de gestos",
            imagen
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camara.release()
    detector.close()
    cv2.destroyAllWindows()
