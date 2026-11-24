
import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS = BASE_DIR / "assets"


class Acercamientos:

    def __init__(self, ancho, alto):

        self.ancho = ancho
        self.alto = alto
        self.actual = None
        self.zonas_cajon = {}
        self.rect_tarjeta = pygame.Rect(550, 400, 110, 80)
        self.imagenes = {}

        nombres = [
            "cajon",
            "cajon_vacio",
            "cajon_sin_llave",
            "cajon_sin_nota",
            "reloj",
            "reloj_resuelto",
            "baul_cerrado",
            "baul_abierto",
            "baul_vacio",
            "baul_sin_objetos",
            "escaner",
            "escaner_autorizado",
            "puerta_abierta"
        ]

        for nombre in nombres:

            ruta = ASSETS / "acercamientos" / f"{nombre}.png"

            imagen = pygame.image.load(str(ruta)).convert_alpha()

            escala = min(
                ancho / imagen.get_width(),
                alto / imagen.get_height()
            )

            dimensiones = (
                int(imagen.get_width() * escala),
                int(imagen.get_height() * escala)
            )

            self.imagenes[nombre] = pygame.transform.smoothscale(
                imagen, dimensiones
            )

        ruta_boton = (
            ASSETS / "interfaz" / "botones" / "btn_regresar.png"
        )

        imagen_boton = pygame.image.load(
            str(ruta_boton)
        ).convert_alpha()

        self.btn_regresar = pygame.transform.smoothscale(
            imagen_boton, (70, 70)
        )

        self.rect_regresar = pygame.Rect(20, 20, 70, 70)

        # Zonas clicables provisionales
        self.zonas = {
            "frontal": {
                "cajon": pygame.Rect(645, 500, 250, 50)
            },
            "izquierda": {
                "reloj": pygame.Rect(405, 20, 215, 665)
            },
            "derecha": {},
            "posterior": {
                "baul_cerrado": pygame.Rect(108, 410, 370, 245),
                "escaner": pygame.Rect(915, 230, 90, 150)
            }
        }

        # Activar para visualizar las zonas clicables
        self.rect_puerta = pygame.Rect(545, 65, 345, 495)
        self.debug = False

    def abrir(self, nombre):

        if nombre in self.imagenes:
            self.actual = nombre

    def cerrar(self):

        self.actual = None

    def esta_abierto(self):

        return self.actual is not None

    def manejar_clic(self, posicion, vista):

        if self.esta_abierto():

            if self.rect_regresar.collidepoint(posicion):
                self.cerrar()

            return True

        for nombre, rect in self.zonas.get(vista, {}).items():

            if rect.collidepoint(posicion):

                self.abrir(nombre)
                return True

        return False

    def dibujar_zonas(self, pantalla, vista):

        if not self.debug:
            return

        fuente = pygame.font.Font(None, 24)

        for nombre, rect in self.zonas.get(vista, {}).items():

            pygame.draw.rect(
                pantalla, (255, 200, 60), rect, 2
            )

            texto = fuente.render(
                nombre, True, (255, 220, 100)
            )

            pantalla.blit(texto, (rect.x, rect.y))

    def imagen_cajon(self, estado):
        if estado.llave_obtenida and estado.nota_obtenida:
            return "cajon_vacio"
        if estado.llave_obtenida:
            return "cajon_sin_llave"
        if estado.nota_obtenida:
            return "cajon_sin_nota"
        return "cajon"

    def actualizar_zonas_cajon(self, estado):
        nombre = self.imagen_cajon(estado)
        imagen = self.imagenes[nombre]
        rect = imagen.get_rect(center=(self.ancho // 2, self.alto // 2))
        self.zonas_cajon = {}
        def zona(x, y, w, h):
            return pygame.Rect(rect.x + int(x*rect.w), rect.y + int(y*rect.h),
                               int(w*rect.w), int(h*rect.h))
        if not estado.llave_obtenida:
            self.zonas_cajon["llave"] = zona(.17, .43, .18, .37)
        if not estado.nota_obtenida:
            self.zonas_cajon["nota"] = zona(.35, .21, .47, .48)

    def zona_baul(self):
        if self.actual not in ("baul_cerrado", "baul_abierto"):
            return None
        imagen = self.imagenes[self.actual]
        rect = imagen.get_rect(center=(self.ancho // 2, self.alto // 2))
        x, y, w, h = ((.53, .45, .12, .19) if self.actual == "baul_cerrado"
                      else (.72, .22, .12, .32))
        return pygame.Rect(rect.x + int(x*rect.w), rect.y + int(y*rect.h),
                           int(w*rect.w), int(h*rect.h))

    def dibujar(self, pantalla, estado):

        if not self.esta_abierto():
            return

        pantalla.fill((24, 13, 19))

        imagen = self.imagenes[self.imagen_cajon(estado) if self.actual == "cajon" else ("reloj_resuelto" if self.actual == "reloj" and estado.reloj_resuelto else self.actual)]

        rect = imagen.get_rect(
            center=(self.ancho // 2, self.alto // 2)
        )

        pantalla.blit(imagen, rect)

        if not estado.juego_completado:
            pantalla.blit(self.btn_regresar, self.rect_regresar)

    def actualizar_cursor(self, posicion, vista):
        if self.esta_abierto():
            zona = self.zona_baul()
            interactivo = self.rect_regresar.collidepoint(posicion) or (zona is not None and zona.collidepoint(posicion))

        else:
            interactivo = (vista == "posterior" and self.rect_puerta.collidepoint(posicion)) or any(
                rect.collidepoint(posicion)
                for rect in self.zonas.get(vista, {}).values()
            )

        if interactivo:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
