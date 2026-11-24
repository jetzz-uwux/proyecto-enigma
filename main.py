
import pygame
import cv2
import time
from juego.inventario import NOTA
from interacciones.aruco import LectorArUco
from juego.habitacion import Habitacion
from juego.acercamientos import Acercamientos
from juego.interfaz import Interfaz
from juego.estado import EstadoJuego
from juego.inventario import Inventario
from juego.camara_ui import CamaraUI
from juego.orientacion import Orientacion
from juego.ayuda_gestual import AyudaGestual
from interacciones.gestos import LectorGestos
from juego.reloj import RelojInteractivo

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
camara_ui = CamaraUI()
ayuda_gestual = AyudaGestual()
orientacion = Orientacion()
gestos = LectorGestos()
reloj_ui = RelojInteractivo(ANCHO, ALTO, lector=gestos)
# El lector ArUco es el único propietario de la webcam.
reloj_ui.camara_disponible = True
ayuda_gestual.activa = False
camara_activa = False
intento_camara = False
frame = None
fuente_prueba = pygame.font.Font(None, 25)
inventario = Inventario(interfaz.espacios)
acercamientos.actualizar_zonas_cajon(estado)

MENSAJES = {
    "cajon": "Parece que alguien dejó algunos objetos aquí.",
    "reloj": "Faltan las manecillas. Investiga los muebles del camerino.",
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

# Cada zona contiene un rectángulo, un objeto opcional y un mensaje.
ZONAS_INVESTIGACION = {
    'izquierda': [
        (pygame.Rect(720, 380, 135, 95), 'manecilla_hora', 'Encontraste la manecilla de la hora entre los libros.'),
        (pygame.Rect(145, 175, 225, 115), None, 'Un cuadro de una antigua función. No hay nada detrás.'),
        (pygame.Rect(900, 345, 105, 125), None, 'Un globo antiguo. No parece esconder nada.'),
    ],
    'derecha': [
        (pygame.Rect(115, 175, 105, 50), 'manecilla_minuto', 'Encontraste la manecilla de los minutos en el estante de las máscaras.'),
        (pygame.Rect(100, 230, 225, 95), None, 'Abanicos de antiguas funciones. No encuentro nada útil.'),
        (pygame.Rect(550, 105, 290, 65), None, 'Sombrereras llenas de polvo. Están vacías.'),
        (pygame.Rect(600, 220, 170, 300), None, 'Un vestido de escena. No hay nada en sus pliegues.'),
    ],
}

def zonas_disponibles():
    if acercamientos.esta_abierto():
        return []
    return [z for z in ZONAS_INVESTIGACION.get(habitacion.vista_actual, [])
            if z[1] is None or z[1] not in estado.manecillas_encontradas]


def zona_investigable(pos):
    if any(r.collidepoint(pos) for r in (interfaz.rect_dialogo,
            interfaz.rect_inventario, interfaz.rect_microfono,
            habitacion.rect_izquierda, habitacion.rect_derecha)):
        return None
    if modo == 'objetos' and frame is not None and pygame.Rect(95, 5, 220, 165).collidepoint(pos):
        return None
    return next((z for z in zonas_disponibles() if z[0].collidepoint(pos)), None)

MARCADORES = {0: 'llave', 1: 'nota', 2: 'tarjeta', 3: 'manecilla_hora', 4: 'manecilla_minuto'}
INSCRIPCION = 'Un dedo señala el destino; cinco anuncian la libertad. Respeta el orden y el último telón caerá.'
ultimo_id = None
inicio_id = 0.0
procesado_id = None
modo_anterior = None
modo = None
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
                    interfaz.cambiar_mensaje("Primero encuentra la nota y coloca ambas manecillas.")

            elif evento.key == pygame.K_F3 and acercamientos.debug and acercamientos.actual == "baul_abierto":
                if estado.validar_palabra("TELÓN"):
                    interfaz.cambiar_mensaje("La tarjeta ha sido revelada. Recógela.")
                else:
                    interfaz.cambiar_mensaje("Primero resuelve el reloj.")

            elif evento.key == pygame.K_F5 and acercamientos.debug:
                orientacion.solicitar(estado, habitacion, acercamientos, interfaz)

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

                if (acercamientos.actual == "reloj" and len(estado.manecillas_colocadas) == 2
                        and estado.nota_obtenida and not estado.reloj_resuelto
                        and reloj_ui.manejar_clic(evento.pos)):
                    if reloj_ui.resuelto and estado.resolver_reloj():
                        interfaz.cambiar_mensaje("El último secreto permanece detrás del TELÓN.")
                    continue

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
                            interfaz.cambiar_mensaje("Has recogido la tarjeta. Su reverso parece ocultar algo. Investiga su marcador.")
                        continue
                    zona_baul = acercamientos.zona_baul()
                    if zona_baul is not None and zona_baul.collidepoint(evento.pos):
                        if acercamientos.actual == "baul_cerrado":
                            if not estado.llave_obtenida:
                                interfaz.cambiar_mensaje("Necesito encontrar una llave para abrir el baúl.")
                            elif inventario.seleccionado != "llave":
                                interfaz.cambiar_mensaje("Presenta el marcador de la llave o selecciónala en el inventario.")
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

                    hallazgo = zona_investigable(evento.pos)
                    if hallazgo:
                        _, nombre, mensaje = hallazgo
                        if nombre is None:
                            interfaz.cambiar_mensaje(mensaje)
                        elif inventario.agregar(nombre):
                            estado.manecillas_encontradas.add(nombre)
                            interfaz.cambiar_mensaje(mensaje + ' Presenta su marcador en el reloj.')
                        continue
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

                            if acercamientos.actual == "reloj" and len(estado.manecillas_colocadas) == 2:
                                mensaje = "Consulta la nota y ajusta la hora." if not estado.reloj_resuelto else "El último secreto permanece detrás del TELÓN."
                            elif acercamientos.actual == "reloj" and estado.manecillas_encontradas:
                                mensaje = "Presenta los marcadores de las manecillas encontradas."
                            interfaz.cambiar_mensaje("Presenta la tarjeta física frente a la cámara." if acercamientos.actual == "escaner" and estado.tarjeta_obtenida else mensaje)

    if not acercamientos.esta_abierto() and (
        vista_anterior != habitacion.vista_actual
        or acercamiento_anterior is not None
    ):
        interfaz.cambiar_mensaje(MENSAJES_VISTA[habitacion.vista_actual])

    modo = 'escaner' if acercamientos.actual == 'escaner' and estado.tarjeta_obtenida and not estado.acceso_autorizado else 'objetos' if not estado.juego_completado else None
    if modo != modo_anterior:
        lector.reiniciar_escaneo()
        ultimo_id = procesado_id = None
        modo_anterior = modo
    necesita_camara = modo is not None
    if necesita_camara:
        if not intento_camara:
            intento_camara = True
            camara_activa = lector.iniciar()
            if not camara_activa:
                interfaz.cambiar_mensaje("No se pudo abrir la cámara. Regresa e inténtalo de nuevo.")
        if camara_activa:
            _, frame = lector.detectar(escaneo_activo=modo == 'escaner')
            if modo == 'objetos':
                ids = lector.ids_detectados
                actual_id = ids[0] if len(ids) == 1 else None
                if actual_id != ultimo_id:
                    ultimo_id = actual_id
                    inicio_id = time.monotonic()
                    procesado_id = None
                if actual_id is not None and actual_id != procesado_id and time.monotonic() - inicio_id >= 0.8:
                    procesado_id = actual_id
                    nombre = MARCADORES.get(actual_id)
                    if nombre not in inventario.objetos:
                        interfaz.cambiar_mensaje('Primero encuentra el objeto correspondiente.' if nombre else 'Marcador desconocido.')
                    else:
                        inventario.seleccionado = nombre
                        if nombre == 'nota':
                            interfaz.cambiar_mensaje(NOTA)
                        elif nombre == 'tarjeta':
                            estado.inscripcion_revelada = True
                            interfaz.cambiar_mensaje(INSCRIPCION)
                        elif nombre.startswith('manecilla') and acercamientos.actual == 'reloj':
                            estado.manecillas_colocadas.add(nombre)
                            interfaz.cambiar_mensaje('Ambas manecillas colocadas. Consulta la nota.' if len(estado.manecillas_colocadas) == 2 else 'Manecilla colocada. Falta la otra.')
                        else:
                            interfaz.cambiar_mensaje('Objeto seleccionado: ' + nombre.replace('_', ' '))
            if modo == 'escaner' and lector.autorizado:
                estado.acceso_autorizado = True
                acercamientos.abrir("escaner_autorizado")
                interfaz.cambiar_mensaje("Acceso autorizado. Falta confirmar la apertura de la puerta.")
    else:
        if camara_activa:
            lector.cerrar()
        camara_activa = False
        intento_camara = False
        frame = None

    reloj_listo = (acercamientos.actual == "reloj" and len(estado.manecillas_colocadas) == 2 and estado.nota_obtenida and not estado.reloj_resuelto)
    if reloj_listo and frame is not None:
        datos = gestos.reconocer_datos(frame)
        reloj_ui._procesar_gesto(datos)
        if reloj_ui.resuelto and estado.resolver_reloj():
            interfaz.cambiar_mensaje("El último secreto permanece detrás del TELÓN.")

    if acercamientos.esta_abierto():

        if reloj_listo and not estado.reloj_resuelto:
            reloj_ui.debug = acercamientos.debug
            reloj_ui.dibujar(pantalla)
            pantalla.blit(acercamientos.btn_regresar, acercamientos.rect_regresar)
        else:
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
        camara_ui.dibujar(pantalla, frame, (340, 45, 600, 385))
        pygame.draw.rect(pantalla, (30, 20, 25), (440, 425, 400, 60))
        pantalla.blit(fuente_prueba.render(lector.estado, True, (240, 220, 180)), (450, 432))
        pygame.draw.rect(pantalla, (90, 75, 65), (450, 460, 380, 12))
        pygame.draw.rect(pantalla, (90, 220, 120), (450, 460, int(380*lector.progreso), 12))
    if acercamientos.debug:
        for zona, _, _ in zonas_disponibles():
            pygame.draw.rect(pantalla, (255, 215, 0), zona, 2, border_radius=5)
    if modo == 'objetos' and frame is not None:
        camara_ui.dibujar(pantalla, frame, (95, 5, 220, 145))
        pantalla.blit(fuente_prueba.render('Marcador del objeto obtenido', True, (240,220,180)), (95, 145))
    interfaz.dibujar(pantalla)
    if not estado.juego_completado:
        modo_ayuda = "reloj" if acercamientos.actual == "reloj" and not estado.reloj_resuelto else "puerta" if estado.acceso_autorizado and habitacion.vista_actual == "posterior" and not acercamientos.esta_abierto() else "exploracion"
        ayuda_gestual.dibujar(pantalla, modo_ayuda)
    inventario.dibujar(pantalla)
    orientacion.dibujar(pantalla, estado, habitacion, acercamientos, zonas_disponibles(), interfaz, inventario)

    posicion = pygame.mouse.get_pos()
    if estado.juego_completado:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.display.flip()
        reloj.tick(FPS)
        continue

    hallazgo = zona_investigable(posicion)
    if reloj_listo and not estado.reloj_resuelto and reloj_ui.rect_confirmar.collidepoint(posicion):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif hallazgo:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif (acercamientos.actual == "baul_abierto" and estado.palabra_validada and not estado.tarjeta_obtenida and acercamientos.rect_tarjeta.collidepoint(posicion)) or inventario.objeto_en(posicion) or (
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

gestos.cerrar()
lector.cerrar()
pygame.quit()
