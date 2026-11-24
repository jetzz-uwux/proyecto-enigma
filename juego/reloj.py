"""Acertijo gestual del reloj para ENIGMA: Ecos del Olvido."""

import math
from pathlib import Path

import pygame

from interacciones.gestos import LectorGestos

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS = BASE_DIR / "assets"


class RelojInteractivo:
    """Permite ajustar las manecillas a las 10:25 mediante gestos.

    Uso básico desde main.py:
        reloj_ui = RelojInteractivo(ANCHO, ALTO)
        reloj_ui.iniciar()                 # al abrir el acercamiento "reloj"
        reloj_ui.actualizar()              # una vez por frame mientras esté abierto
        reloj_ui.dibujar(pantalla)         # en lugar de acercamientos.dibujar
        reloj_ui.cerrar()                  # al salir del acercamiento

    El estado global se actualiza desde main.py cuando reloj_ui.resuelto=True.
    """

    TOLERANCIA_GRADOS = 7.0

    def __init__(self, ancho, alto, lector=None):
        self.ancho = ancho
        self.alto = alto
        self.lector = lector or LectorGestos()
        self._lector_externo = lector is not None

        self.imagen_reloj = self._cargar("acercamientos/reloj.png")
        self.imagen_resuelto = self._cargar("acercamientos/reloj_resuelto.png")
        self.imagen_hora = self._cargar("objetos/manecilla_hora.png")
        self.imagen_minuto = self._cargar("objetos/manecilla_minuto.png")

        # Se mantiene el tamaño nativo del fondo (560 x 473) para conservar
        # la relación entre el centro del dial y los pivotes de las agujas.
        self.rect_reloj = self.imagen_reloj.get_rect(
            center=(ancho // 2, min(alto // 2 - 10, 320))
        )
        self.centro = (
            self.rect_reloj.x + 280,
            self.rect_reloj.y + 236,
        )

        # Centros de los remaches/pivotes, medidos en los PNG originales.
        self.pivote_hora = (54, 373)
        self.pivote_minuto = (56, 443)

        self.angulo_hora = 270.0
        self.angulo_minuto = 0.0
        self.seleccionada = None
        self.gesto_actual = "SIN MANO"
        self.cursor_indice = None
        self.resuelto = False
        self.camara_disponible = False
        self.mensaje = "Levanta el índice y acércalo a una manecilla."
        self._gesto_anterior = "SIN MANO"
        self._comprobacion_realizada = False
        self._ultimo_frame_camara = None

        self.fuente = pygame.font.SysFont("georgia", 19)
        self.fuente_pequena = pygame.font.SysFont("georgia", 15)

    def _cargar(self, relativo):
        ruta = ASSETS / relativo
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró el asset del reloj: {ruta}")
        return pygame.image.load(str(ruta)).convert_alpha()

    def iniciar(self):
        """Inicia la webcam solo cuando se entra al acertijo."""
        if self.resuelto:
            return True
        self.camara_disponible = self.lector.iniciar()
        if self.camara_disponible:
            self.mensaje = "Índice: selecciona y mueve. Puño: suelta. Mano abierta: comprueba."
        else:
            self.mensaje = "No se pudo abrir la webcam. Cierra otras aplicaciones que la utilicen."
        return self.camara_disponible

    def cerrar(self):
        """Libera la webcam al salir del acercamiento."""
        self.lector.cerrar()
        self.camara_disponible = False
        self.seleccionada = None
        self.cursor_indice = None
        self._gesto_anterior = "SIN MANO"

    @staticmethod
    def _normalizar_angulo(angulo):
        return angulo % 360.0

    @staticmethod
    def _angulo_desde_punto(centro, punto):
        dx = punto[0] - centro[0]
        dy = centro[1] - punto[1]
        # 0 grados = 12; aumenta en sentido horario.
        return (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0

    @staticmethod
    def _distancia_punto_segmento(punto, inicio, fin):
        px, py = punto
        ax, ay = inicio
        bx, by = fin
        dx, dy = bx - ax, by - ay
        longitud2 = dx * dx + dy * dy
        if longitud2 == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / longitud2))
        proy = (ax + t * dx, ay + t * dy)
        return math.hypot(px - proy[0], py - proy[1])

    def _longitud(self, nombre):
        return 100 if nombre == "hora" else 133

    def _punta(self, nombre):
        angulo = self.angulo_hora if nombre == "hora" else self.angulo_minuto
        rad = math.radians(angulo)
        longitud = self._longitud(nombre)
        return (
            self.centro[0] + math.sin(rad) * longitud,
            self.centro[1] - math.cos(rad) * longitud,
        )

    def _seleccionar_cercana(self, punto):
        opciones = []
        for nombre in ("hora", "minuto"):
            distancia = self._distancia_punto_segmento(
                punto, self.centro, self._punta(nombre)
            )
            punta = self._punta(nombre)
            distancia_punta = math.hypot(punto[0] - punta[0], punto[1] - punta[1])
            opciones.append((distancia, distancia_punta, nombre))
        distancia, _, nombre = min(opciones)
        if distancia <= 34:
            self.seleccionada = nombre
            self.mensaje = (
                "Moviendo manecilla de minutos." if nombre == "minuto"
                else "Moviendo manecilla de horas."
            )
            return True
        self.mensaje = "Acerca el índice a una de las manecillas para seleccionarla."
        return False

    def _mover_a(self, punto):
        if self.seleccionada is None:
            return
        angulo = self._angulo_desde_punto(self.centro, punto)
        if self.seleccionada == "hora":
            self.angulo_hora = angulo
        else:
            self.angulo_minuto = angulo

    def _posicion_indice_pantalla(self, normalizada):
        """Mapea el área completa de la webcam al área útil del reloj."""
        nx, ny = normalizada
        radio_x, radio_y = 225, 225
        return (
            self.centro[0] + (nx - 0.5) * 2 * radio_x,
            self.centro[1] + (ny - 0.5) * 2 * radio_y,
        )

    def _procesar_gesto(self, datos):
        gesto = datos["gesto"]
        self.gesto_actual = gesto
        indice = datos.get("indice")
        if indice is not None:
            self.cursor_indice = self._posicion_indice_pantalla(indice)
        else:
            self.cursor_indice = None

        if self.resuelto:
            self._gesto_anterior = gesto
            return

        if gesto == "INDICE LEVANTADO" and self.cursor_indice is not None:
            if self.seleccionada is None:
                self._seleccionar_cercana(self.cursor_indice)
            else:
                self._mover_a(self.cursor_indice)

        elif gesto == "PUNO CERRADO":
            if self.seleccionada is not None:
                self.seleccionada = None
                self.mensaje = "Manecilla liberada. Selecciona la otra cuando quieras."

        elif gesto == "MANO ABIERTA":
            # Comprobar solo al entrar en este gesto, no 60 veces por segundo.
            if self._gesto_anterior != "MANO ABIERTA":
                self.seleccionada = None
                self.comprobar_hora()

        self._gesto_anterior = gesto

    def actualizar(self):
        """Procesa un frame de cámara. Llamar una vez por iteración del juego."""
        if not self.camara_disponible or self.resuelto:
            return
        datos = self.lector.leer()
        self._ultimo_frame_camara = datos.get("imagen")
        if datos["gesto"] == "ERROR DE CAMARA":
            self.mensaje = "Se perdió la conexión con la webcam. Sal y vuelve a entrar al reloj."
        elif datos["gesto"] == "CAMARA INACTIVA":
            self.mensaje = "La cámara está inactiva."
        else:
            self._procesar_gesto(datos)

    def comprobar_hora(self):
        """Comprueba los ángulos objetivo: 10:25."""
        objetivo_minuto = 150.0       # 25 minutos: 25 * 6 grados.
        objetivo_hora = 312.5         # 10 * 30 + 25 * 0.5 grados.
        error_minuto = abs((self.angulo_minuto - objetivo_minuto + 180) % 360 - 180)
        error_hora = abs((self.angulo_hora - objetivo_hora + 180) % 360 - 180)

        if (error_minuto <= self.TOLERANCIA_GRADOS and
                error_hora <= self.TOLERANCIA_GRADOS):
            self.resuelto = True
            self.seleccionada = None
            self.mensaje = "El último secreto permanece detrás del TELÓN."
            return True

        self.mensaje = "Esa no es la hora correcta. La nota indica las 10:25. Inténtalo de nuevo."
        return False

    def dibujar(self, pantalla):
        """Dibuja el reloj interactivo sin reemplazar el HUD del juego."""
        pantalla.fill((24, 13, 19))
        fondo = self.imagen_resuelto if self.resuelto else self.imagen_reloj
        pantalla.blit(fondo, self.rect_reloj)

        if self.resuelto:
            # El PNG resuelto ya incluye ambas agujas y evita pequeñas
            # diferencias visuales con la ilustración final aprobada.
            pass
        else:
            self._dibujar_manecilla(
                pantalla, self.imagen_minuto, self.pivote_minuto,
                self.angulo_minuto
            )
            self._dibujar_manecilla(
                pantalla, self.imagen_hora, self.pivote_hora,
                self.angulo_hora
            )

        # Instrucciones discretas en la parte superior.
        panel = pygame.Surface((self.ancho - 370, 62), pygame.SRCALPHA)
        panel.fill((15, 8, 13, 205))
        pantalla.blit(panel, (340, 12))
        texto = self.fuente.render("EL TIEMPO DETENIDO", True, (239, 197, 133))
        pantalla.blit(texto, (355, 18))
        instruccion = self.fuente_pequena.render(self.mensaje, True, (245, 225, 190))
        pantalla.blit(instruccion, (355, 43))

        if self.cursor_indice is not None and not self.resuelto:
            pygame.draw.circle(pantalla, (255, 225, 130),
                               (int(self.cursor_indice[0]), int(self.cursor_indice[1])),
                               9, 2)
            pygame.draw.circle(pantalla, (255, 225, 130),
                               (int(self.cursor_indice[0]), int(self.cursor_indice[1])),
                               3)

        if not self.camara_disponible and not self.resuelto:
            aviso = self.fuente_pequena.render(
                "Webcam no disponible", True, (255, 170, 150)
            )
            pantalla.blit(aviso, (self.ancho - aviso.get_width() - 25, 90))

    def _dibujar_manecilla(self, pantalla, imagen, pivote, angulo):
        """Rota el PNG manteniendo fijo su pivote inferior sobre el centro."""
        # El dibujo original apunta en diagonal; compensar su orientación.
        es_hora = imagen is self.imagen_hora
        punta = (116, 20) if es_hora else (210, 4)
        dx, dy = punta[0] - pivote[0], punta[1] - pivote[1]
        angulo_original = math.degrees(math.atan2(dx, -dy))
        escala = self._longitud("hora" if es_hora else "minuto") / math.hypot(dx, dy)
        rotacion = angulo_original - angulo
        rotada = pygame.transform.rotozoom(imagen, rotacion, escala)
        centro_original = pygame.Vector2(imagen.get_width() / 2,
                                         imagen.get_height() / 2)
        vector_pivote = (pygame.Vector2(pivote) - centro_original) * escala
        # Las coordenadas de pantalla tienen Y positiva hacia abajo.
        vector_rotado = vector_pivote.rotate(-rotacion)
        centro_rotado = pygame.Vector2(self.centro) - vector_rotado
        rect = rotada.get_rect(center=(round(centro_rotado.x),
                                       round(centro_rotado.y)))
        pantalla.blit(rotada, rect)

    def reiniciar(self):
        """Restablece el acertijo para pruebas; no modifica EstadoJuego."""
        self.angulo_hora = 270.0
        self.angulo_minuto = 0.0
        self.seleccionada = None
        self.resuelto = False
        self.mensaje = "Levanta el índice y acércalo a una manecilla."
        self._gesto_anterior = "SIN MANO"
