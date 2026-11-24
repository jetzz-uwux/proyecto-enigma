"""Prueba visual independiente del módulo gestual del reloj ENIGMA.

Ejecutar desde la raíz del proyecto:
    python probar_reloj.py

Teclas:
    ESC: salir
    R: reiniciar ángulos del acertijo
"""

import pygame
from juego.reloj import RelojInteractivo

ANCHO, ALTO = 1280, 720
FPS = 30


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("ENIGMA - Prueba del acertijo del reloj")
    reloj_fps = pygame.time.Clock()

    modulo = RelojInteractivo(ANCHO, ALTO)
    if not modulo.iniciar():
        print("No se pudo abrir la webcam. Revisa permisos o cierra otras aplicaciones.")

    ejecutando = True
    try:
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando = False
                    elif evento.key == pygame.K_r:
                        modulo.reiniciar()

            modulo.actualizar()
            modulo.dibujar(pantalla)
            pygame.display.flip()
            reloj_fps.tick(FPS)
    finally:
        modulo.cerrar()
        pygame.quit()


if __name__ == "__main__":
    main()
