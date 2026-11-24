import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS = BASE_DIR / "assets"


class Habitacion:

    def __init__(self, ancho, alto):

        self.ancho = ancho
        self.alto = alto

        self.vistas = [
            "frontal",
            "derecha",
            "posterior",
            "izquierda"
        ]

        self.indice = 0
        self.escenarios = {}

        for vista in self.vistas:

            ruta = (
                ASSETS / "escenarios" / f"vista_{vista}.png"
            )

            imagen = pygame.image.load(str(ruta)).convert()

            self.escenarios[vista] = pygame.transform.smoothscale(
                imagen,
                (ancho, alto)
            )

        self.rect_izquierda = pygame.Rect(
            20, alto // 2 - 40, 80, 80
        )

        self.rect_derecha = pygame.Rect(
            ancho - 100, alto // 2 - 40, 80, 80
        )

        self.btn_izquierda = self.cargar_boton(
            "btn_izquierda.png"
        )

        self.btn_derecha = self.cargar_boton(
            "btn_derecha.png"
        )

    def cargar_boton(self, nombre):

        ruta = ASSETS / "interfaz" / "botones" / nombre

        imagen = pygame.image.load(str(ruta)).convert_alpha()

        return pygame.transform.smoothscale(
            imagen, (80, 80)
        )

    @property
    def vista_actual(self):

        return self.vistas[self.indice]

    def girar_izquierda(self):

        self.indice = (self.indice - 1) % len(self.vistas)

    def girar_derecha(self):

        self.indice = (self.indice + 1) % len(self.vistas)

    def manejar_clic(self, posicion):

        if self.rect_izquierda.collidepoint(posicion):

            self.girar_izquierda()
            return True

        if self.rect_derecha.collidepoint(posicion):

            self.girar_derecha()
            return True

        return False

    def dibujar(self, pantalla):

        pantalla.blit(
            self.escenarios[self.vista_actual],
            (0, 0)
        )

        pantalla.blit(
            self.btn_izquierda,
            self.rect_izquierda
        )

        pantalla.blit(
            self.btn_derecha,
            self.rect_derecha
        )
