"""Cursor virtual; reutiliza los datos de MediaPipe, sin abrir otra cámara."""
import time
import pygame

class CursorGestual:
    def __init__(self, ancho, alto):
        self.ancho, self.alto = ancho, alto
        self.pos = (ancho / 2, alto / 2)
        self.visible = False
        self.armado = False
        self.desde_indice = None
        self.desde_puno = None
        self.ultimo_indice = 0.0
        self.flash = 0.0
        self.historial = []

    def reiniciar(self):
        self.visible = self.armado = False
        self.desde_indice = self.desde_puno = None
        self.historial.clear()

    def actualizar(self, datos, ahora=None):
        ahora = time.monotonic() if ahora is None else ahora
        gesto = datos.get('gesto')
        indice = datos.get('indice')
        if gesto == 'INDICE LEVANTADO' and indice is not None:
            if self.desde_indice is None:
                self.desde_indice = ahora
            self.desde_puno = None
            objetivo = tuple(max(0, min(1, (v - .12) / .76)) * (n - 1)
                             for v, n in zip(indice, (self.ancho, self.alto)))
            self.pos = tuple(a + .32 * (b-a) for a,b in zip(self.pos, objetivo)) if self.visible else objetivo
            self.visible = True
            self.ultimo_indice = ahora
            self.historial.append((ahora, self.pos))
            self.historial = [(t,p) for t,p in self.historial if ahora-t <= .4]
            if ahora - self.desde_indice >= .18:
                self.armado = True
        else:
            self.desde_indice = None
            if gesto == 'PUNO CERRADO' and self.armado and ahora-self.ultimo_indice <= .65:
                if self.desde_puno is None:
                    self.desde_puno = ahora
                    anteriores = [p for t,p in self.historial if ahora-t >= .10]
                    if anteriores:
                        self.pos = anteriores[-1]
                if ahora-self.desde_puno >= .10:
                    self.armado = False
                    self.flash = ahora + .25
                    return tuple(map(round,self.pos))
            else:
                self.desde_puno = None
                if gesto in ('SIN MANO','MANO ABIERTA') or ahora-self.ultimo_indice > .65:
                    self.armado = False
            if ahora-self.ultimo_indice > 1.0:
                self.visible = False
        return None

    def dibujar(self, pantalla):
        if not self.visible:
            return
        p = tuple(map(round,self.pos))
        pygame.draw.circle(pantalla, (10,24,29), p, 15, 5)
        pygame.draw.circle(pantalla, (86,244,224), p, 15, 2)
        pygame.draw.circle(pantalla, (186,255,245), p, 3)
        if time.monotonic() < self.flash:
            pygame.draw.circle(pantalla, (255,255,255), p, 22, 2)
