from pathlib import Path
import pygame
import cv2


class CamaraUI:
    """Presentación visual; no abre ni controla la cámara física."""
    def __init__(self):
        ruta = Path(__file__).resolve().parents[1] / 'assets/interfaz/indicadores/marco_escaner.png'
        self.marco = pygame.image.load(str(ruta)).convert_alpha()
        self.cache = {}

    def dibujar(self, pantalla, frame, rect):
        rect = pygame.Rect(rect)
        if rect.size not in self.cache:
            self.cache[rect.size] = pygame.transform.smoothscale(self.marco, rect.size)
        pantalla.blit(self.cache[rect.size], rect)
        if frame is None:
            return
        # El asset tiene un centro opaco: el video se dibuja encima,
        # dentro de las marcas interiores, sin tapar el borde dorado.
        interior = pygame.Rect(rect.x + round(rect.w * .155),
                               rect.y + round(rect.h * .29),
                               round(rect.w * .69), round(rect.h * .47))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        video = pygame.image.frombuffer(rgb.tobytes(), (w, h), 'RGB')
        escala = min(interior.w / w, interior.h / h)
        video = pygame.transform.smoothscale(video, (max(1, round(w * escala)), max(1, round(h * escala))))
        pantalla.blit(video, video.get_rect(center=interior.center))
