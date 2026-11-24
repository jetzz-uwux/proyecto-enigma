
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELO = BASE_DIR / "modelos" / "hand_landmarker.task"

class LectorGestos:
    """Detecta una mano y devuelve gesto y coordenadas normalizadas del índice."""

    def __init__(self, indice_camara=0, ancho_camara=640, alto_camara=480,
                 espejo=True):
        self.indice_camara = indice_camara
        self.ancho_camara = ancho_camara
        self.alto_camara = alto_camara
        self.espejo = espejo
        self.camara = None
        self.ultima_imagen = None
        self.ultimo_resultado = None

        ruta_modelo = (
            Path(__file__).resolve().parent.parent
            / "modelos" / "hand_landmarker.task"
        )
        if not ruta_modelo.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo de MediaPipe: {ruta_modelo}"
            )

        self.ruta_modelo = ruta_modelo
        self.detector = None
        self._crear_detector()

    def _crear_detector(self):

        print("Cargando modelo de MediaPipe...")
        print("Ruta:", self.ruta_modelo)
        print("Existe:", self.ruta_modelo.exists())
        print("Tamaño:", self.ruta_modelo.stat().st_size, "bytes")

        opciones = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_buffer=self.ruta_modelo.read_bytes()
            ),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55,
            min_tracking_confidence=0.55,
        )

        self.detector = vision.HandLandmarker.create_from_options(
            opciones
        )

        print("Modelo de MediaPipe cargado correctamente.")


    def iniciar(self):
        """Abre la webcam. Devuelve True si quedó disponible."""
        if self.detector is None:
            self._crear_detector()
        if self.camara is not None and self.camara.isOpened():
            return True

        self.camara = cv2.VideoCapture(self.indice_camara, cv2.CAP_DSHOW)
        if not self.camara.isOpened():
            self.camara.release()
            self.camara = cv2.VideoCapture(self.indice_camara)

        if not self.camara.isOpened():
            self.camara.release()
            self.camara = None
            return False

        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho_camara)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto_camara)
        return True

    @staticmethod
    def _clasificar(mano):
        """Clasifica los cuatro dedos largos; no depende de la orientación X."""
        puntas = (8, 12, 16, 20)
        articulaciones_pip = (6, 10, 14, 18)
        extendidos = [
            mano[p].y < mano[a].y - 0.015
            for p, a in zip(puntas, articulaciones_pip)
        ]

        if all(extendidos):
            return "MANO ABIERTA"
        if not any(extendidos):
            return "PUNO CERRADO"
        if extendidos == [True, False, False, False]:
            return "INDICE LEVANTADO"
        return "GESTO NO RECONOCIDO"

    def reconocer_datos(self, imagen_bgr):
        """Procesa un frame BGR y devuelve gesto, índice y landmarks.

        indice contiene x/y normalizados entre 0 y 1. La imagen se espeja
        antes del análisis si espejo=True, para que el movimiento se sienta
        como un espejo frente al jugador.
        """
        if imagen_bgr is None:
            return {
                "gesto": "SIN MANO", "indice": None,
                "landmarks": None, "imagen": None
            }

        imagen = cv2.flip(imagen_bgr, 1) if self.espejo else imagen_bgr.copy()
        rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        imagen_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        resultado = self.detector.detect(imagen_mp)

        if not resultado.hand_landmarks:
            datos = {
                "gesto": "SIN MANO", "indice": None,
                "landmarks": None, "imagen": imagen
            }
            self.ultimo_resultado = datos
            return datos

        mano = resultado.hand_landmarks[0]
        punta_indice = mano[8]
        datos = {
            "gesto": self._clasificar(mano),
            "indice": (float(punta_indice.x), float(punta_indice.y)),
            "landmarks": mano,
            "imagen": imagen,
        }
        self.ultimo_resultado = datos
        return datos

    def reconocer(self, imagen_bgr):
        """Compatibilidad con la versión previa: devuelve solo el gesto."""
        return self.reconocer_datos(imagen_bgr)["gesto"]

    def leer(self):
        """Lee y procesa un frame de la webcam. Devuelve un diccionario."""
        if self.camara is None or not self.camara.isOpened():
            return {
                "gesto": "CAMARA INACTIVA", "indice": None,
                "landmarks": None, "imagen": None
            }

        correcto, frame = self.camara.read()
        if not correcto:
            return {
                "gesto": "ERROR DE CAMARA", "indice": None,
                "landmarks": None, "imagen": None
            }

        datos = self.reconocer_datos(frame)
        self.ultima_imagen = datos["imagen"]
        return datos

    def cerrar(self):
        if self.camara is not None:
            self.camara.release()
            self.camara = None
        self.ultima_imagen = None
        self.ultimo_resultado = None

        if self.detector is not None:
            self.detector.close()
            self.detector = None
