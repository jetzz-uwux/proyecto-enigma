
import cv2
import mediapipe as mp

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class LectorGestos:
    def __init__(self):
        ruta_modelo = (
            Path(__file__).resolve().parent.parent
            / "modelos"
            / "hand_landmarker.task"
        )

        opciones = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=str(ruta_modelo)
            ),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=1
        )

        self.detector = (
            vision.HandLandmarker.create_from_options(
                opciones
            )
        )

    def reconocer(self, imagen_bgr):
        if imagen_bgr is None:
            return "SIN MANO"

        imagen_rgb = cv2.cvtColor(
            imagen_bgr,
            cv2.COLOR_BGR2RGB
        )

        imagen_mp = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagen_rgb
        )

        resultado = self.detector.detect(imagen_mp)

        if not resultado.hand_landmarks:
            return "SIN MANO"

        mano = resultado.hand_landmarks[0]

        puntas = [8, 12, 16, 20]
        articulaciones = [6, 10, 14, 18]

        dedos = []

        for punta, articulacion in zip(
            puntas, articulaciones
        ):
            dedos.append(
                mano[punta].y < mano[articulacion].y
            )

        if all(dedos):
            return "MANO ABIERTA"

        if not any(dedos):
            return "PUNO CERRADO"

        if dedos == [True, False, False, False]:
            return "INDICE LEVANTADO"

        return "GESTO NO RECONOCIDO"

    def cerrar(self):
        self.detector.close()
