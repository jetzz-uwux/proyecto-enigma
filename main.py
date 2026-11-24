
import pygame
import cv2
from interacciones.aruco import LectorArUco
from juego.habitacion import Habitacion
from juego.acercamientos import Acercamientos
from juego.interfaz import Interfaz
from juego.estado import EstadoJuego
from juego.inventario import Inventario

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
estado = EstadoJuego()
lector = LectorArUco()
camara_activa = False
intento_camara = False
frame = None
fuente_prueba = pygame.font.Font(None, 25)
inventario = Inventario(interfaz.espacios)
acercamientos.actualizar_zonas_cajon(estado)

MENSAJES = {
    "cajon": "Parece que alguien dejó algunos objetos aquí.",
    "reloj": "Un antiguo reloj. Quizás la hora tenga algún significado.",
    "baul_cerrado": "El baúl está cerrado. Necesito una llave.",
    "baul_abierto": "Solo el eco de la última función podrá revelar lo que aquí se esconde.",
    "escaner": "Necesito una tarjeta para autorizar el acceso.",
    "escaner_autorizado": "Acceso autorizado. Falta confirmar la apertura de la puerta."
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

        elif estado.juego_completado:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                ejecutando = False

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:

                if acercamientos.esta_abierto():
                    acercamientos.cerrar()
                else:
                    ejecutando = False

            elif evento.key == pygame.K_F4 and acercamientos.debug and habitacion.vista_actual == "posterior" and not acercamientos.esta_abierto():
                if estado.confirmar_salida():
                    acercamientos.abrir("puerta_abierta")
                    interfaz.cambiar_mensaje("Los secretos del camerino han sido revelados. Finalmente, eres libre.")
                else:
                    interfaz.cambiar_mensaje("Primero autoriza el acceso en la terminal.")

            elif evento.key == pygame.K_F2 and acercamientos.debug and acercamientos.actual == "reloj":
                if estado.resolver_reloj():
                    interfaz.cambiar_mensaje("El último secreto permanece detrás del TELÓN.")
                else:
                    interfaz.cambiar_mensaje("Primero encuentra la nota.")

            elif evento.key == pygame.K_F3 and acercamientos.debug and acercamientos.actual == "baul_abierto":
                if estado.validar_palabra("TELÓN"):
                    interfaz.cambiar_mensaje("La tarjeta ha sido revelada. Recógela.")
                else:
                    interfaz.cambiar_mensaje("Primero resuelve el reloj.")

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

                if interfaz.rect_inventario.collidepoint(evento.pos):
                    mensaje = inventario.seleccionar(evento.pos)
                    if mensaje:
                        interfaz.cambiar_mensaje(mensaje)
                    continue

                if interfaz.manejar_clic(evento.pos):
                    continue

                if acercamientos.esta_abierto():

                    if acercamientos.actual == "baul_abierto" and estado.palabra_validada and not estado.tarjeta_obtenida and acercamientos.rect_tarjeta.collidepoint(evento.pos):
                        if inventario.agregar("tarjeta"):
                            estado.tarjeta_obtenida = True
                            interfaz.cambiar_mensaje("Has recogido la tarjeta de acceso.")
                        continue
                    zona_baul = acercamientos.zona_baul()
                    if zona_baul is not None and zona_baul.collidepoint(evento.pos):
                        if acercamientos.actual == "baul_cerrado":
                            if not estado.llave_obtenida:
                                interfaz.cambiar_mensaje("Necesito encontrar una llave para abrir el baúl.")
                            elif inventario.seleccionado != "llave":
                                interfaz.cambiar_mensaje("Selecciona la llave dorada del inventario.")
                            else:
                                estado.baul_abierto = True
                                inventario.seleccionado = None
                                acercamientos.abrir("baul_abierto")
                                interfaz.cambiar_mensaje(MENSAJES["baul_abierto"])
                        else:
                            if not estado.reloj_resuelto:
                                interfaz.cambiar_mensaje("Quizás el reloj esconda la palabra que necesito.")
                            else:
                                interfaz.cambiar_mensaje("El reconocimiento de voz aún no está integrado.")
                        continue

                    if acercamientos.actual == "cajon":
                        recogido = False
                        for nombre, rect in acercamientos.zonas_cajon.items():
                            if rect.collidepoint(evento.pos) and inventario.agregar(nombre):
                                if nombre == "llave":
                                    estado.llave_obtenida = True
                                else:
                                    estado.nota_obtenida = True
                                interfaz.cambiar_mensaje("Has recogido la " + ("llave dorada." if nombre == "llave" else "nota. Puedes leerla desde el inventario."))
                                recogido = True
                                break
                        if recogido:
                            acercamientos.actualizar_zonas_cajon(estado)
                            continue

                    acercamientos.manejar_clic(
                        evento.pos,
                        habitacion.vista_actual
                    )

                else:

                    if habitacion.vista_actual == "posterior" and acercamientos.rect_puerta.collidepoint(evento.pos):
                        interfaz.cambiar_mensaje("Confirma la apertura mediante el gesto indicado." if estado.acceso_autorizado else "La puerta está bloqueada. Autoriza el acceso en la terminal.")
                        continue

                    if not habitacion.manejar_clic(evento.pos):

                        acercamientos.manejar_clic(
                            evento.pos,
                            habitacion.vista_actual
                        )

                        if acercamientos.esta_abierto():

                            if acercamientos.actual == "cajon":
                                estado.cajon_abierto = True
                            if acercamientos.actual == "baul_cerrado" and estado.baul_abierto:
                                acercamientos.abrir("baul_abierto")
                            if acercamientos.actual == "escaner" and estado.acceso_autorizado:
                                acercamientos.abrir("escaner_autorizado")
                            mensaje = MENSAJES.get(
                                acercamientos.actual,
                                ""
                            )

                            interfaz.cambiar_mensaje("Presenta la tarjeta física frente a la cámara." if acercamientos.actual == "escaner" and estado.tarjeta_obtenida else mensaje)

    if not acercamientos.esta_abierto() and (
        vista_anterior != habitacion.vista_actual
        or acercamiento_anterior is not None
    ):
        interfaz.cambiar_mensaje(MENSAJES_VISTA[habitacion.vista_actual])

    necesita_camara = acercamientos.actual == "escaner" and estado.tarjeta_obtenida and not estado.acceso_autorizado
    if necesita_camara:
        if not intento_camara:
            intento_camara = True
            camara_activa = lector.iniciar()
            if not camara_activa:
                interfaz.cambiar_mensaje("No se pudo abrir la cámara. Regresa e inténtalo de nuevo.")
        if camara_activa:
            _, frame = lector.detectar(escaneo_activo=True)
            if lector.autorizado:
                estado.acceso_autorizado = True
                acercamientos.abrir("escaner_autorizado")
                interfaz.cambiar_mensaje("Acceso autorizado. Falta confirmar la apertura de la puerta.")
    else:
        if camara_activa:
            lector.cerrar()
        camara_activa = False
        intento_camara = False
        frame = None

    if acercamientos.esta_abierto():

        acercamientos.dibujar(pantalla, estado)
        zona_baul = acercamientos.zona_baul()
        if acercamientos.debug and zona_baul is not None:
            pygame.draw.rect(pantalla, (255, 200, 60), zona_baul, 2)
        if acercamientos.actual == "cajon":
            for nombre, rect in acercamientos.zonas_cajon.items():
                if nombre not in inventario.objetos:
                    if acercamientos.debug:
                        pygame.draw.rect(pantalla, (255, 200, 60), rect, 2)

    else:

        habitacion.dibujar(pantalla)

        acercamientos.dibujar_zonas(
            pantalla,
            habitacion.vista_actual
        )

    if acercamientos.actual == "baul_abierto" and estado.palabra_validada and not estado.tarjeta_obtenida:
        imagen = inventario.imagen_ajustada("tarjeta", acercamientos.rect_tarjeta)
        pantalla.blit(imagen, imagen.get_rect(center=acercamientos.rect_tarjeta.center))
    if acercamientos.actual == "escaner" and frame is not None and camara_activa:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video = pygame.image.frombuffer(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")
        video = pygame.transform.smoothscale(video, (400, 300))
        pantalla.blit(video, (440, 120))
        pygame.draw.rect(pantalla, (30, 20, 25), (440, 425, 400, 60))
        pantalla.blit(fuente_prueba.render(lector.estado, True, (240, 220, 180)), (450, 432))
        pygame.draw.rect(pantalla, (90, 75, 65), (450, 460, 380, 12))
        pygame.draw.rect(pantalla, (90, 220, 120), (450, 460, int(380*lector.progreso), 12))
    interfaz.dibujar(pantalla)
    inventario.dibujar(pantalla)

    posicion = pygame.mouse.get_pos()
    if estado.juego_completado:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.display.flip()
        reloj.tick(FPS)
        continue

    if (acercamientos.actual == "baul_abierto" and estado.palabra_validada and not estado.tarjeta_obtenida and acercamientos.rect_tarjeta.collidepoint(posicion)) or inventario.objeto_en(posicion) or (
        acercamientos.actual == "cajon" and any(
            nombre not in inventario.objetos and rect.collidepoint(posicion)
            for nombre, rect in acercamientos.zonas_cajon.items()
        )
    ):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    elif interfaz.rect_microfono.collidepoint(posicion):

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

lector.cerrar()
pygame.quit()
