
import cv2
from interacciones.aruco import LectorArUco


def main():

    lector = LectorArUco()

    if not lector.iniciar():

        print("No fue posible iniciar la prueba.")
        return

    print("=" * 45)
    print("ENIGMA: PRUEBA DE ESCANER ARUCO")
    print("=" * 45)
    print("Tarjeta valida: ID 2")
    print("Tarjeta incorrecta: ID 3")
    print("Mantener tarjeta visible durante 1.5 segundos.")
    print("Presiona R para reiniciar.")
    print("Presiona Q para salir.")
    print("=" * 45)

    try:

        while True:

            detectados, imagen = lector.detectar()

            if imagen is None:

                print("No se pudo obtener la imagen.")
                break

            alto, ancho = imagen.shape[:2]

            if lector.autorizado:

                color = (80, 220, 100)

            elif lector.estado == "TARJETA INCORRECTA":

                color = (60, 60, 255)

            else:

                color = (255, 220, 0)

            # Panel inferior
            cv2.rectangle(
                imagen,
                (0, alto - 105),
                (ancho, alto),
                (25, 25, 25),
                -1
            )

            # Estado del escaner
            cv2.putText(
                imagen,
                lector.estado,
                (20, alto - 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            # Fondo de la barra de progreso
            cv2.rectangle(
                imagen,
                (20, alto - 55),
                (ancho - 20, alto - 35),
                (75, 75, 75),
                -1
            )

            ancho_barra = ancho - 40

            progreso = int(
                ancho_barra * lector.progreso
            )

            if progreso > 0:

                cv2.rectangle(
                    imagen,
                    (20, alto - 55),
                    (20 + progreso, alto - 35),
                    color,
                    -1
                )

            # Instrucciones
            cv2.putText(
                imagen,
                "R: Reiniciar | Q: Salir",
                (20, alto - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (230, 230, 230),
                1
            )

            cv2.imshow(
                "ENIGMA - Escaner ArUco",
                imagen
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break

            elif tecla == ord("r"):

                lector.reiniciar_escaneo()

                print("Escaner reiniciado.")

    finally:

        lector.cerrar()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
