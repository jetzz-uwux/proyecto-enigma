
import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS = BASE_DIR / "assets" / "interfaz"


class Interfaz:

    def __init__(self, ancho, alto):

        self.ancho = ancho
        self.alto = alto

        self.fuente = pygame.font.SysFont("georgia", 20)
        self.fuente_titulo = pygame.font.SysFont(
            "georgia", 17, bold=True
        )

        self.mensaje = (
            "La puerta está cerrada... Quizás encuentre "
            "algo en este camerino que me permita salir."
        )

        # Panel de dialogo
        self.panel_dialogo = self.cargar_imagen(
            "paneles/panel_dialogo.png",
            (710, 140)
        )

        self.rect_dialogo = pygame.Rect(
            15, alto - 150, 710, 140
        )

        # Panel de inventario
        self.panel_inventario = self.cargar_imagen(
            "paneles/panel_inventario.png",
            (530, 140)
        )

        self.rect_inventario = pygame.Rect(
            ancho - 545, alto - 150, 530, 140
        )

        # Boton de microfono
        self.btn_microfono = self.cargar_imagen(
            "botones/btn_microfono.png",
            (65, 65)
        )

        self.rect_microfono = pygame.Rect(
            ancho - 85, 20, 65, 65
        )

        # Espacios del inventario
        self.espacios = []

        for i in range(5):

            rect = pygame.Rect(
                self.rect_inventario.x + [55, 142, 228, 314, 400][i],
                self.rect_inventario.y + 62,
                74,
                45
            )

            self.espacios.append(rect)

        self.debug = False
        self.voz_disponible = False
        self.estado_voz = "espera"
        self.fuente_voz = pygame.font.SysFont("georgia", 15)

    def actualizar_voz(self, disponible, estado="espera"):
        self.voz_disponible = disponible
        self.estado_voz = estado

    def cargar_imagen(self, nombre, dimensiones):

        ruta = ASSETS / nombre

        imagen = pygame.image.load(
            str(ruta)
        ).convert_alpha()

        return pygame.transform.smoothscale(
            imagen, dimensiones
        )

    def cambiar_mensaje(self, mensaje):

        self.mensaje = mensaje

    def dividir_texto(self, texto, ancho_maximo):

        palabras = texto.split()
        lineas = []
        linea = ""

        for palabra in palabras:

            prueba = f"{linea} {palabra}".strip()

            if self.fuente.size(prueba)[0] <= ancho_maximo:

                linea = prueba

            else:

                if linea:
                    lineas.append(linea)

                linea = palabra

        if linea:
            lineas.append(linea)

        return lineas

    def manejar_clic(self, posicion):

        if self.rect_microfono.collidepoint(posicion):

            self.cambiar_mensaje(
                "El micrófono todavía no está disponible."
            )

            return True

        if self.rect_inventario.collidepoint(posicion):

            return True

        if self.rect_dialogo.collidepoint(posicion):

            return True

        return False

    def dibujar(self, pantalla):

        pantalla.blit(
            self.panel_dialogo,
            self.rect_dialogo
        )

        pantalla.blit(
            self.panel_inventario,
            self.rect_inventario
        )

        pantalla.blit(
            self.btn_microfono,
            self.rect_microfono
        )

        if self.voz_disponible:
            etiquetas = {"espera": "Di ‘pista’", "escuchando": "Escuchando...", "correcto": "Reconocido", "incorrecto": "Intenta de nuevo"}
            colores = {"espera": (240,220,180), "escuchando": (255,215,100), "correcto": (120,230,150), "incorrecto": (255,140,130)}
            color = colores.get(self.estado_voz, colores["espera"])
            texto = self.fuente_voz.render(etiquetas.get(self.estado_voz, etiquetas["espera"]), True, color)
            rect = texto.get_rect(topright=(self.rect_microfono.right, self.rect_microfono.bottom + 4))
            pygame.draw.rect(pantalla, (35,22,28), rect.inflate(12,6), border_radius=4)
            pantalla.blit(texto, rect)
            if self.estado_voz == "escuchando":
                pygame.draw.rect(pantalla, color, self.rect_microfono, 2, border_radius=8)

        # Texto del dialogo
        lineas = self.dividir_texto(
            self.mensaje, 540
        )

        for i, linea in enumerate(lineas):

            texto = self.fuente.render(
                linea,
                True,
                (245, 225, 190)
            )

            pantalla.blit(
                texto,
                (
                    self.rect_dialogo.x + 85,
                    self.rect_dialogo.y + 84 - len(lineas) * 12 + i * 24
                )
            )

        # Zonas provisionales del inventario
        if self.debug:

            for i, rect in enumerate(self.espacios):

                pygame.draw.rect(
                    pantalla,
                    (220, 180, 90),
                    rect,
                    1
                )

                numero = self.fuente_titulo.render(
                    str(i + 1),
                    True,
                    (220, 180, 90)
                )

                pantalla.blit(
                    numero,
                    numero.get_rect(center=rect.center)
                )
