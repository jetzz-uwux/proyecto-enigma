
import pygame
from juego.habitacion import Habitacion
from juego.acercamientos import Acercamientos
from juego.interfaz import Interfaz

pygame.init()

ANCHO = 1280
ALTO = 720
FPS = 60

pantalla = pygame.display.set_mode((ANCHO, ALTO))

pygame.display.set_caption(
    "ENIGMA: Ecos del Olvido"
)

reloj = pygame.time.Clock()

habitacion = Habitacion(ANCHO, ALTO)
acercamientos = Acercamientos(ANCHO, ALTO)
interfaz = Interfaz(ANCHO, ALTO)

MENSAJES = {
    "cajon": "Parece que alguien dejó algunos objetos aquí.",
    "reloj": "Un antiguo reloj. Quizás la hora tenga algún significado.",
    "baul_cerrado": "El baúl está cerrado. Necesito una llave.",
    "escaner": "Necesito una tarjeta para autorizar el acceso."
}

MENSAJES_VISTA = {
    "frontal": "Un tocador antiguo. Quizás haya algo útil en sus cajones.",
    "izquierda": "El reloj parece haberse detenido.",
    "derecha": "El vestuario conserva recuerdos de antiguas funciones.",
    "posterior": "La puerta está cerrada. Hay un baúl y una terminal de acceso."
}

ejecutando = True

while ejecutando:

    vista_anterior = habitacion.vista_actual
    acercamiento_anterior = acercamientos.actual

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:

            ejecutando = False

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:

                if acercamientos.esta_abierto():
                    acercamientos.cerrar()
                else:
                    ejecutando = False

            elif evento.key == pygame.K_F1:

                acercamientos.debug = not acercamientos.debug
                interfaz.debug = acercamientos.debug

            elif not acercamientos.esta_abierto():

                if evento.key == pygame.K_LEFT:

                    habitacion.girar_izquierda()

                elif evento.key == pygame.K_RIGHT:

                    habitacion.girar_derecha()

        elif evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:

                if interfaz.manejar_clic(evento.pos):
                    continue

                if acercamientos.esta_abierto():

                    acercamientos.manejar_clic(
                        evento.pos,
                        habitacion.vista_actual
                    )

                else:

                    if not habitacion.manejar_clic(evento.pos):

                        acercamientos.manejar_clic(
                            evento.pos,
                            habitacion.vista_actual
                        )

                        if acercamientos.esta_abierto():

                            mensaje = MENSAJES.get(
                                acercamientos.actual,
                                ""
                            )

                            interfaz.cambiar_mensaje(mensaje)

    if not acercamientos.esta_abierto() and (
        vista_anterior != habitacion.vista_actual
        or acercamiento_anterior is not None
    ):
        interfaz.cambiar_mensaje(MENSAJES_VISTA[habitacion.vista_actual])

    if acercamientos.esta_abierto():

        acercamientos.dibujar(pantalla)

    else:

        habitacion.dibujar(pantalla)

        acercamientos.dibujar_zonas(
            pantalla,
            habitacion.vista_actual
        )

    interfaz.dibujar(pantalla)

    posicion = pygame.mouse.get_pos()

    if interfaz.rect_microfono.collidepoint(posicion):

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND
        )

    elif (
        interfaz.rect_dialogo.collidepoint(posicion)
        or interfaz.rect_inventario.collidepoint(posicion)
    ):

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_ARROW
        )

    elif (
        not acercamientos.esta_abierto()
        and (
            habitacion.rect_izquierda.collidepoint(posicion)
            or habitacion.rect_derecha.collidepoint(posicion)
        )
    ):

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND
        )

    else:

        acercamientos.actualizar_cursor(
            posicion,
            habitacion.vista_actual
        )

    pygame.display.flip()

    reloj.tick(FPS)

pygame.quit()
