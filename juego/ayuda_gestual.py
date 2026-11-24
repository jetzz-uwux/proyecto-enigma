"""Ayuda contextual; activar únicamente con controles reales integrados."""
from pathlib import Path
import pygame

class AyudaGestual:
    def __init__(self):
        self.activa = False
        self.fuente = pygame.font.SysFont('georgia', 15)
        ruta = Path(__file__).resolve().parent.parent / 'assets/interfaz/gestos'
        self.iconos = {}
        for nombre in ('indice', 'puno', 'mano_abierta'):
            img = pygame.image.load(str(ruta / f'gesto_{nombre}.png')).convert_alpha()
            img = pygame.transform.smoothscale(img, (round(img.get_width()*min(48/img.get_width(),48/img.get_height())), round(img.get_height()*min(48/img.get_width(),48/img.get_height()))))
            self.iconos[nombre] = img

    def dibujar(self, pantalla, modo='exploracion'):
        if not self.activa:
            return
        opciones = {'exploracion': [('indice','Mover cursor'),('puno','Seleccionar')], 'reloj': [('indice','Mover manecilla'),('puno','Soltar'),('mano_abierta','Confirmar hora')], 'puerta': [('indice','Seleccionar'),('mano_abierta','Confirmar 1 s')]}
        filas = opciones.get(modo, [])
        if not filas:
            return
        panel = pygame.Rect(18, 100, 210, 12+56*len(filas))
        pygame.draw.rect(pantalla,(40,24,30),panel,border_radius=8)
        pygame.draw.rect(pantalla,(190,150,85),panel,2,border_radius=8)
        for i,(nombre,texto) in enumerate(filas):
            y=panel.y+6+i*56
            pantalla.blit(self.iconos[nombre],self.iconos[nombre].get_rect(center=(panel.x+30,y+24)))
            pantalla.blit(self.fuente.render(texto,True,(245,225,190)),(panel.x+58,y+16))
