"""Tutoriales contextuales: no alteran el estado de los acertijos."""
from pathlib import Path
import pygame

PAGINAS = {
 'inicio': [('Mueve el cursor','Levanta el índice y mueve tu mano frente a la cámara para recorrer la pantalla.','gestos/gesto_indice.png'),('Selecciona','Apunta al objeto o botón y cierra el puño para hacer clic. También puedes usar el ratón.','gestos/gesto_puno.png'),('Solicita ayuda','Selecciona el micrófono y di «pista». El botón ? permite volver a consultar las instrucciones.','botones/btn_microfono.png')],
 'aruco': [('Objetos y marcadores','Después de encontrar un objeto, presenta su marcador físico frente a la cámara.','../objetos/llave.png'),('Mantén el marcador visible','Muestra un marcador a la vez, sin tapar sus esquinas. Retíralo después de que el juego lo reconozca.','indicadores/marco_escaner.png')],
 'reloj': [('Selecciona una manecilla','Cuando hayas colocado ambas manecillas mediante sus marcadores y encontrado la nota, acerca el índice a una manecilla.','gestos/gesto_indice.png'),('Ajusta la posición','Mueve el índice alrededor de la esfera hasta alcanzar la posición deseada.','../objetos/manecilla_minuto.png'),('Libera la manecilla','Cierra el puño para dejar fija la manecilla. Repite con la otra.','gestos/gesto_puno.png'),('Confirma la hora','Mantén la palma abierta durante 0.7 segundos para cambiar al modo cursor. Selecciona Confirmar hora con el puño. Repite la palma para volver a las manecillas.','gestos/gesto_mano_abierta.png')],
 'voz': [('Activa el micrófono','Selecciona el micrófono del baúl cuando hayas descubierto la palabra secreta.','botones/btn_microfono.png'),('Habla con claridad','Cuando aparezca Escuchando, pronuncia la palabra secreta. Si no se reconoce, vuelve a intentarlo.','indicadores/indicador_voz.png')],
 'escaner': [('Presenta la tarjeta','Después de obtener la tarjeta virtual, muestra su marcador físico frente a la cámara.','../objetos/tarjeta.png'),('Espera la autorización','Mantén el marcador visible hasta completar la barra de progreso. Después regresa y selecciona la puerta.','indicadores/estado_correcto.png')],
 'puerta': [('El último desafío','Consulta la inscripción de la tarjeta y reproduce los gestos en el orden indicado. Mantén cada gesto hasta que el progreso avance.','../objetos/tarjeta.png')]
}

class Tutoriales:
    def __init__(self, ancho, alto):
        self.actual = None
        self.pagina = 0
        self.vistos = set()
        self.panel = pygame.Rect(0,0,760,470)
        self.panel.center = (ancho//2,alto//2)
        self.rect_ayuda = pygame.Rect(ancho-145,28,44,44)
        self.anterior = pygame.Rect(self.panel.x+30,self.panel.bottom-65,150,40)
        self.omitir = pygame.Rect(self.panel.centerx-70,self.panel.bottom-65,140,40)
        self.siguiente = pygame.Rect(self.panel.right-190,self.panel.bottom-65,160,40)
        self.titulo = pygame.font.SysFont('georgia',30,bold=True)
        self.fuente = pygame.font.SysFont('georgia',23)
        self.pequena = pygame.font.SysFont('georgia',18)
        self.imagenes = {}
        self.base = Path(__file__).resolve().parent.parent/'assets'/'interfaz'
    @property
    def activo(self):
        return self.actual is not None
    def abrir(self, nombre, manual=False):
        if self.activo or (nombre in self.vistos and not manual): return False
        self.actual, self.pagina = nombre, 0
        return True
    def cerrar(self):
        if self.activo: self.vistos.add(self.actual)
        self.actual = None
    def clic(self,pos):
        if not self.activo: return False
        if self.omitir.collidepoint(pos): self.cerrar()
        elif self.anterior.collidepoint(pos): self.pagina=max(0,self.pagina-1)
        elif self.siguiente.collidepoint(pos):
            if self.pagina+1 == len(PAGINAS[self.actual]): self.cerrar()
            else: self.pagina+=1
        return True
    def boton(self,pantalla,rect,texto):
        pygame.draw.rect(pantalla,(105,34,53),rect,border_radius=7)
        pygame.draw.rect(pantalla,(208,169,100),rect,2,border_radius=7)
        img=self.pequena.render(texto,True,(255,232,188))
        pantalla.blit(img,img.get_rect(center=rect.center))
    def dibujar(self,pantalla):
        self.boton(pantalla,self.rect_ayuda,'?')
        if not self.activo: return
        sombra=pygame.Surface(pantalla.get_size(),pygame.SRCALPHA); sombra.fill((10,5,12,175)); pantalla.blit(sombra,(0,0))
        p=self.panel
        pygame.draw.rect(pantalla,(65,22,37),p,border_radius=12)
        pygame.draw.rect(pantalla,(209,169,100),p,3,border_radius=12)
        pygame.draw.rect(pantalla,(132,91,52),p.inflate(-16,-16),1,border_radius=8)
        paginas=PAGINAS[self.actual]; titulo, texto, ruta=paginas[self.pagina]
        def centrado(f,t,y):
            s=f.render(t,True,(249,224,177)); pantalla.blit(s,s.get_rect(midtop=(p.centerx,y)))
        centrado(self.pequena,f'TUTORIAL  •  {self.pagina+1} / {len(paginas)}',p.y+22)
        centrado(self.titulo,titulo,p.y+53)
        if ruta not in self.imagenes:
            try:
                im=pygame.image.load(str(self.base/ruta)).convert_alpha(); escala=min(155/im.get_width(),155/im.get_height()); self.imagenes[ruta]=pygame.transform.smoothscale(im,(max(1,round(im.get_width()*escala)),max(1,round(im.get_height()*escala))))
            except (OSError,pygame.error): self.imagenes[ruta]=None
        im=self.imagenes[ruta]
        if im: pantalla.blit(im,im.get_rect(center=(p.centerx,p.y+175)))
        lineas=[]; linea=''
        for palabra in texto.split():
            candidato=(linea+' '+palabra).strip()
            if self.fuente.size(candidato)[0]>p.width-80 and linea: lineas.append(linea); linea=palabra
            else: linea=candidato
        if linea: lineas.append(linea)
        for i,l in enumerate(lineas): centrado(self.fuente,l,p.y+265+i*28)
        if self.pagina: self.boton(pantalla,self.anterior,'Anterior')
        self.boton(pantalla,self.omitir,'Omitir')
        self.boton(pantalla,self.siguiente,'Finalizar' if self.pagina+1==len(paginas) else 'Siguiente')
