"""Ayuda contextual y resaltado temporal, sin dependencias de voz."""
import time
import pygame
from juego.pistas import obtener_pista, mensaje_pista

class Orientacion:
    def __init__(self):
        self.hasta = 0

    def solicitar(self, estado, habitacion, acercamientos, interfaz):
        mensaje = mensaje_pista(estado, habitacion.vista_actual)
        destino, objetivo, _ = obtener_pista(estado)
        if acercamientos.esta_abierto() and (destino != habitacion.vista_actual or objetivo not in (acercamientos.actual, 'tarjeta') and not (objetivo == 'baul_cerrado' and acercamientos.actual == 'baul_abierto')):
            mensaje = 'Regresa a la habitación. ' + mensaje
        interfaz.cambiar_mensaje(mensaje)
        self.hasta = time.monotonic() + 3

    def dibujar(self, pantalla, estado, habitacion, acercamientos, zonas, interfaz, inventario):
        if time.monotonic() >= self.hasta or estado.juego_completado:
            return
        destino, objetivo, _ = obtener_pista(estado)
        vista, actual = habitacion.vista_actual, acercamientos.actual
        rects = []
        if actual:
            if destino != vista:
                rects = [acercamientos.rect_regresar]
            elif objetivo == 'cajon' and actual == 'cajon':
                rects = list(acercamientos.zonas_cajon.values())
            elif objetivo == 'reloj' and actual == 'reloj':
                faltan = {'manecilla_hora', 'manecilla_minuto'} - estado.manecillas_colocadas
                rects = [r for n,r in zip(inventario.objetos, inventario.espacios) if n in faltan or (not faltan and n == 'nota')]
            elif objetivo == 'tarjeta' and actual == 'baul_abierto':
                rects = [acercamientos.rect_tarjeta]
            elif objetivo in ('baul_cerrado','baul_abierto') and actual == objetivo:
                rects = [acercamientos.zona_baul()]
            elif objetivo == 'escaner' and actual == 'escaner':
                rects = [pygame.Rect(340,45,600,385)]
            else:
                rects = [acercamientos.rect_regresar]
        elif destino != vista and destino:
            distancia = (habitacion.vistas.index(destino)-habitacion.vistas.index(vista)) % 4
            rects = [habitacion.rect_izquierda if distancia == 3 else habitacion.rect_derecha]
        elif objetivo in ('manecilla_hora','manecilla_minuto'):
            rects = [r for r,n,_ in zonas if n == objetivo]
        elif objetivo == 'puerta':
            rects = [acercamientos.rect_puerta]
        elif objetivo == 'inscripcion':
            rects = [r for n,r in zip(inventario.objetos,inventario.espacios) if n == 'tarjeta']
        else:
            rects = [acercamientos.zonas.get(vista,{}).get('baul_cerrado' if objetivo in ('tarjeta','baul_abierto') else objetivo)]
        for rect in rects:
            if rect is not None:
                pygame.draw.rect(pantalla, (255,215,100), rect, 3, border_radius=5)
