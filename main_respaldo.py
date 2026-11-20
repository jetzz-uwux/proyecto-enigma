
import pygame
import cv2
from interacciones.aruco import LectorArUco

pygame.init()

ANCHO, ALTO = 1000, 650

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ENIGMA: Ecos del Olvido")

reloj = pygame.time.Clock()

COLOR_FONDO = (28, 32, 43)
COLOR_PARED = (47, 53, 67)
COLOR_OBJETO = (196, 155, 92)
COLOR_TEXTO = (240, 235, 225)
COLOR_INVENTARIO = (40, 44, 55)
COLOR_VALIDO = (105, 205, 145)

fuente = pygame.font.SysFont("arial", 24)
fuente_pequena = pygame.font.SysFont("arial", 18)

objetos = [
    {
        "nombre": "Llave",
        "rect": pygame.Rect(220, 350, 65, 40),
        "recogido": False
    },
    {
        "nombre": "Tarjeta",
        "rect": pygame.Rect(600, 300, 90, 50),
        "recogido": False
    }
]

inventario = []

mensaje = "Recoge un objeto y muestra su tarjeta a la camara."
objeto_detectado = None

lector = LectorArUco()
camara_activa = lector.iniciar()

if not camara_activa:
    mensaje = "No se pudo iniciar la camara."

ejecutando = True

try:
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    for objeto in objetos:
                        if (
                            not objeto["recogido"]
                            and objeto["rect"].collidepoint(evento.pos)
                        ):
                            objeto["recogido"] = True
                            inventario.append(objeto["nombre"])

                            mensaje = (
                                f"Objeto obtenido: {objeto['nombre']}"
                            )
                            break

        # Reconocimiento de tarjetas
        objeto_detectado = None
        imagen_camara = None

        if camara_activa:
            detectados, imagen_camara = lector.detectar()

            for nombre in detectados:
                if nombre in inventario:
                    objeto_detectado = nombre
                    break

        # Dibujar habitación
        pantalla.fill(COLOR_FONDO)

        pygame.draw.rect(
            pantalla,
            COLOR_PARED,
            (80, 80, 840, 420)
        )

        pygame.draw.rect(
            pantalla,
            (90, 75, 65),
            (440, 260, 120, 240)
        )

        # Dibujar objetos
        for objeto in objetos:
            if not objeto["recogido"]:
                pygame.draw.rect(
                    pantalla,
                    COLOR_OBJETO,
                    objeto["rect"]
                )

                etiqueta = fuente_pequena.render(
                    objeto["nombre"],
                    True,
                    COLOR_TEXTO
                )

                pantalla.blit(
                    etiqueta,
                    (
                        objeto["rect"].x,
                        objeto["rect"].y - 25
                    )
                )

        # Mensaje
        texto_mensaje = fuente_pequena.render(
            mensaje,
            True,
            COLOR_TEXTO
        )

        pantalla.blit(texto_mensaje, (80, 30))

        # Inventario
        pygame.draw.rect(
            pantalla,
            COLOR_INVENTARIO,
            (0, 530, ANCHO, 120)
        )

        titulo = fuente.render(
            "INVENTARIO",
            True,
            COLOR_TEXTO
        )

        pantalla.blit(titulo, (30, 545))

        for i, nombre in enumerate(inventario):
            color = (
                COLOR_VALIDO
                if nombre == objeto_detectado
                else COLOR_TEXTO
            )

            texto = fuente_pequena.render(
                nombre,
                True,
                color
            )

            pantalla.blit(
                texto,
                (40 + i * 150, 595)
            )

        # Mostrar resultado del reconocimiento
        if objeto_detectado is not None:
            texto = fuente_pequena.render(
                f"Tarjeta reconocida: {objeto_detectado}",
                True,
                COLOR_VALIDO
            )

            pantalla.blit(texto, (610, 510))

        # Vista previa de la cámara
        if imagen_camara is not None:
            imagen_rgb = cv2.cvtColor(
                imagen_camara,
                cv2.COLOR_BGR2RGB
            )

            imagen_rgb = cv2.resize(
                imagen_rgb,
                (240, 180)
            )

            superficie_camara = pygame.image.frombuffer(
                imagen_rgb.tobytes(),
                (240, 180),
                "RGB"
            )

            pantalla.blit(
                superficie_camara,
                (680, 90)
            )

        pygame.display.flip()
        reloj.tick(30)

finally:
    lector.cerrar()
    pygame.quit()
