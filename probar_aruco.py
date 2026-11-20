
import cv2

diccionario = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

parametros = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(
    diccionario, parametros
)

objetos = {
    1: "Llave",
    2: "Tarjeta"
}

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    raise RuntimeError("No se pudo abrir la camara.")

print("Camara iniciada. Presiona Q para salir.")

while True:
    correcto, imagen = camara.read()

    if not correcto:
        print("No se pudo leer la imagen.")
        break

    esquinas, ids, _ = detector.detectMarkers(imagen)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(
            imagen, esquinas, ids
        )

        for indice, identificador in enumerate(ids.flatten()):
            nombre = objetos.get(
                int(identificador),
                "Objeto desconocido"
            )

            puntos = esquinas[indice][0]
            x = int(puntos[:, 0].min())
            y = int(puntos[:, 1].min())

            cv2.putText(
                imagen,
                nombre,
                (x, max(25, y - 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("ENIGMA - Reconocimiento ArUco", imagen)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
