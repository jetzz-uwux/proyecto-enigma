
import pygame
from juego.habitacion import Habitacion
from juego.acercamientos import Acercamientos

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

ejecutando = True

while ejecutando:

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

            elif not acercamientos.esta_abierto():

                if evento.key == pygame.K_LEFT:

                    habitacion.girar_izquierda()

                elif evento.key == pygame.K_RIGHT:

                    habitacion.girar_derecha()

        elif evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:

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

        acercamientos.dibujar(pantalla)

    else:

        habitacion.dibujar(pantalla)

        acercamientos.dibujar_zonas(
            pantalla,
            habitacion.vista_actual
        )

    acercamientos.actualizar_cursor(
        pygame.mouse.get_pos(),
        habitacion.vista_actual
    )

    pygame.display.flip()

    reloj.tick(FPS)

pygame.quit()
