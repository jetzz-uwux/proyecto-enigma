
import cv2


class LectorArUco:
    def __init__(self):
        diccionario = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )

        parametros = cv2.aruco.DetectorParameters()

        self.detector = cv2.aruco.ArucoDetector(
            diccionario, parametros
        )

        self.camara = None

        self.objetos = {
            1: "Llave",
            2: "Tarjeta"
        }

    def iniciar(self):
        self.camara = cv2.VideoCapture(0)

        if not self.camara.isOpened():
            self.camara.release()
            self.camara = None
            return False

        return True

    def detectar(self):
        if self.camara is None:
            return [], None

        correcto, imagen = self.camara.read()

        if not correcto:
            return [], None

        esquinas, ids, _ = self.detector.detectMarkers(imagen)

        nombres = []

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(
                imagen, esquinas, ids
            )

            for indice, identificador in enumerate(ids.flatten()):
                nombre = self.objetos.get(int(identificador))

                if nombre is not None:
                    nombres.append(nombre)

                    puntos = esquinas[indice][0]

                    x = int(puntos[:, 0].min())
                    y = int(puntos[:, 1].min())

                    cv2.putText(
                        imagen,
                        nombre,
                        (x, max(25, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

        return nombres, imagen

    def cerrar(self):
        if self.camara is not None:
            self.camara.release()
            self.camara = None
