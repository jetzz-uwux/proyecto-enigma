
import cv2
import time
import numpy as np


class LectorArUco:

    ID_ACCESO = 2
    TIEMPO_CONFIRMACION = 1.5

    def __init__(self):

        self.camara = None

        self.diccionario = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )

        self.parametros = cv2.aruco.DetectorParameters()

        self.detector = cv2.aruco.ArucoDetector(
            self.diccionario,
            self.parametros
        )

        self.ids_detectados = []

        self.inicio_escaneo = None
        self.progreso = 0.0

        self.autorizado = False
        self.estado = "ESPERANDO TARJETA"

    def iniciar(self, indice_camara=0):

        if self.camara is not None:
            if self.camara.isOpened():
                return True

            self.camara.release()

        self.camara = cv2.VideoCapture(
            indice_camara,
            cv2.CAP_DSHOW
        )

        if not self.camara.isOpened():

            self.camara.release()

            self.camara = cv2.VideoCapture(indice_camara)

        if not self.camara.isOpened():

            self.camara.release()
            self.camara = None

            print("No se pudo iniciar la camara.")
            return False

        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("Camara ArUco iniciada correctamente.")

        return True

    def reiniciar_escaneo(self):

        self.inicio_escaneo = None
        self.progreso = 0.0
        self.autorizado = False
        self.estado = "ESPERANDO TARJETA"
        self.ids_detectados = []

    def actualizar_escaneo(self):

        if self.autorizado:

            self.estado = "ACCESO AUTORIZADO"
            self.progreso = 1.0

            return

        tarjeta_valida = self.ID_ACCESO in self.ids_detectados

        if tarjeta_valida:

            if self.inicio_escaneo is None:

                self.inicio_escaneo = time.monotonic()

            transcurrido = (
                time.monotonic() - self.inicio_escaneo
            )

            self.progreso = min(
                transcurrido / self.TIEMPO_CONFIRMACION,
                1.0
            )

            self.estado = "ESCANEANDO TARJETA"

            if transcurrido >= self.TIEMPO_CONFIRMACION:

                self.autorizado = True
                self.progreso = 1.0
                self.estado = "ACCESO AUTORIZADO"

        else:

            self.inicio_escaneo = None
            self.progreso = 0.0

            if self.ids_detectados:

                self.estado = "TARJETA INCORRECTA"

            else:

                self.estado = "ESPERANDO TARJETA"

    def dibujar_realidad_aumentada(
        self,
        imagen,
        esquinas,
        id_marcador
    ):

        puntos = esquinas.reshape((4, 2)).astype(np.int32)

        if id_marcador == self.ID_ACCESO:

            if self.autorizado:

                color = (80, 220, 100)
                texto = "ACCESO AUTORIZADO"

            else:

                color = (255, 220, 0)
                texto = "ESCANEANDO..."

        else:

            color = (60, 60, 255)
            texto = "TARJETA INCORRECTA"

        # Contorno virtual del marcador
        cv2.polylines(
            imagen,
            [puntos],
            True,
            color,
            3,
            cv2.LINE_AA
        )

        # Esquinas resaltadas
        for punto in puntos:

            cv2.circle(
                imagen,
                tuple(punto),
                5,
                color,
                -1
            )

        # Posicion de la etiqueta
        x = max(5, int(np.min(puntos[:, 0])))
        y = max(30, int(np.min(puntos[:, 1])) - 12)

        fuente = cv2.FONT_HERSHEY_SIMPLEX

        (ancho, alto), _ = cv2.getTextSize(
            texto,
            fuente,
            0.5,
            2
        )

        x = max(
            5,
            min(x, imagen.shape[1] - ancho - 12)
        )

        # Fondo de la etiqueta
        cv2.rectangle(
            imagen,
            (x - 4, y - alto - 7),
            (x + ancho + 5, y + 5),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            imagen,
            texto,
            (x, y),
            fuente,
            0.5,
            color,
            2,
            cv2.LINE_AA
        )

    def detectar(self, escaneo_activo=True):

        self.ids_detectados = []

        if self.camara is None:

            self.inicio_escaneo = None
            self.progreso = 0.0

            return [], None

        correcto, imagen = self.camara.read()

        if not correcto:

            self.inicio_escaneo = None
            self.progreso = 0.0
            self.estado = "ERROR DE CAMARA"

            return [], None

        gris = cv2.cvtColor(
            imagen,
            cv2.COLOR_BGR2GRAY
        )

        esquinas, ids, rechazados = (
            self.detector.detectMarkers(gris)
        )

        detectados = []

        if ids is not None:

            self.ids_detectados = [
                int(id_marcador)
                for id_marcador in ids.flatten()
            ]

            for id_marcador in self.ids_detectados:

                if id_marcador == self.ID_ACCESO:

                    if "Tarjeta" not in detectados:
                        detectados.append("Tarjeta")

                else:

                    detectados.append(
                        f"Desconocido_{id_marcador}"
                    )

        if escaneo_activo:

            self.actualizar_escaneo()

            if ids is not None:

                for i, id_marcador in enumerate(
                    self.ids_detectados
                ):

                    self.dibujar_realidad_aumentada(
                        imagen,
                        esquinas[i],
                        id_marcador
                    )

        else:

            self.inicio_escaneo = None

            if not self.autorizado:
                self.progreso = 0.0
                self.estado = "ESCANER INACTIVO"

        return detectados, imagen

    def cerrar(self):

        if self.camara is not None:

            self.camara.release()
            self.camara = None

        self.reiniciar_escaneo()

        print("Camara ArUco cerrada.")
