import pygame
from pathlib import Path

NOTA = 'La última función comenzó a las diez y veinticinco (10:25). Desde entonces, el tiempo se detuvo.'

class Inventario:
    def __init__(self, espacios):
        self.espacios = espacios
        self.objetos = []
        self.seleccionado = None
        carpeta = Path(__file__).resolve().parent.parent / 'assets' / 'objetos'
        self.imagenes = {n: pygame.image.load(str(carpeta / f'{n}.png')).convert_alpha() for n in ('llave', 'nota', 'tarjeta')}

    def agregar(self, nombre):
        if nombre in self.objetos or len(self.objetos) >= len(self.espacios):
            return False
        self.objetos.append(nombre)
        return True

    def objeto_en(self, posicion):
        for nombre, rect in zip(self.objetos, self.espacios):
            if rect.collidepoint(posicion):
                return nombre
        return None

    def seleccionar(self, posicion):
        nombre = self.objeto_en(posicion)
        self.seleccionado = nombre if nombre != self.seleccionado else None
        if nombre == 'nota':
            return NOTA
        if nombre == 'llave':
            return 'Llave dorada seleccionada.' if self.seleccionado else 'Llave deseleccionada.'
        return None

    def imagen_ajustada(self, nombre, rect):
        imagen = self.imagenes[nombre]
        escala = min(rect.width / imagen.get_width(), rect.height / imagen.get_height())
        return pygame.transform.smoothscale(imagen, (max(1, int(imagen.get_width()*escala)), max(1, int(imagen.get_height()*escala))))

    def dibujar(self, pantalla):
        for nombre, rect in zip(self.objetos, self.espacios):
            if nombre == self.seleccionado:
                pygame.draw.rect(pantalla, (255, 220, 130), rect, 2, border_radius=4)
            imagen = self.imagen_ajustada(nombre, rect.inflate(-8, -6))
            pantalla.blit(imagen, imagen.get_rect(center=rect.center))
