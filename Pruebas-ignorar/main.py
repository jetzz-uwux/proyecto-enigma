
import pygame
import cv2
import time
from interacciones.aruco import LectorArUco
from interacciones.gestos import LectorGestos

pygame.init()

ANCHO, ALTO = 1000, 650

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ENIGMA: Ecos del Olvido")

reloj = pygame.time.Clock()

COLOR_FONDO = (28, 32, 43)
COLOR_PARED = (47, 53, 67)
COLOR_OBJETO = (196, 155, 92)
COLOR_TEXTO = (240, 235, 225)
COLOR_INVENTARIO = (40, 44, 55)
COLOR_VALIDO = (105, 205, 145)

fuente = pygame.font.SysFont("arial", 24)
fuente_pequena = pygame.font.SysFont("arial", 18)

# Objetos de la habitación
objetos = [
    {
        "nombre": "Llave",
        "rect": pygame.Rect(170, 310, 65, 40),
        "recogido": False
    },
    {
        "nombre": "Tarjeta",
        "rect": pygame.Rect(600, 300, 90, 50),
        "recogido": False
    }
]

# Cajon que contiene la llave
cajon = pygame.Rect(140, 350, 130, 75)
cajon_abierto = False

# Inventario
inventario = []
mensaje = "Recoge los objetos y muestra sus tarjetas a la camara."
objeto_detectado = None

# Combinación de tarjetas ArUco
combinacion_necesaria = {"Llave", "Tarjeta"}

combinacion_activada = False
inicio_combinacion = None
tiempo_confirmacion = 1.5
progreso_combinacion = 0.0

# Estado de interacción gestual
lector_gestos = LectorGestos()

gesto_actual = "SIN MANO"
gesto_anterior = None
inicio_gesto = None

tiempo_gesto = 1.0
gesto_ejecutado = False

mecanismo_seleccionado = False
puerta_abierta = False

# Iniciar cámara
lector = LectorArUco()
camara_activa = lector.iniciar()

if not camara_activa:
    mensaje = "No se pudo iniciar la camara."

ejecutando = True

try:
    while ejecutando:

        # 1. Eventos de Pygame
        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if cajon.collidepoint(evento.pos):
                        if not cajon_abierto:
                            cajon_abierto = True
                            mensaje = "Has abierto el cajon. Hay una llave."
                        else:
                            mensaje = "El cajon ya esta abierto."

                    else:
                        for objeto in objetos:
                            if (
                                not objeto["recogido"]
                                and objeto["rect"].collidepoint(evento.pos)
                                and (
                                    objeto["nombre"] != "Llave"
                                    or cajon_abierto
                                )
                            ):
                                objeto["recogido"] = True
                                inventario.append(objeto["nombre"])

                                mensaje = (
                                    f"Objeto obtenido: {objeto['nombre']}"
                                )
                                break

        # 2. Reconocimiento de tarjetas ArUco
        objeto_detectado = None
        imagen_camara = None
        detectados = []

        if camara_activa:
            detectados, imagen_camara = lector.detectar()

            for nombre in detectados:
                if nombre in inventario:
                    objeto_detectado = nombre
                    break

            # Reconocer gestos con la misma imagen
            gesto_actual = lector_gestos.reconocer(
                imagen_camara
            )

        else:
            gesto_actual = "SIN MANO"

        # 3. Comprobar combinación simultánea
        ambas_visibles = combinacion_necesaria.issubset(
            set(detectados)
        )

        ambas_recogidas = combinacion_necesaria.issubset(
            set(inventario)
        )

        if not combinacion_activada:

            if ambas_visibles and ambas_recogidas:

                if inicio_combinacion is None:
                    inicio_combinacion = time.monotonic()

                transcurrido = (
                    time.monotonic() - inicio_combinacion
                )

                progreso_combinacion = min(
                    transcurrido / tiempo_confirmacion,
                    1.0
                )

                if transcurrido >= tiempo_confirmacion:
                    combinacion_activada = True
                    mensaje = (
                        "Combinacion correcta: mecanismo activado."
                    )

            else:
                inicio_combinacion = None
                progreso_combinacion = 0.0

        # Interpretar gestos estables
        if gesto_actual != gesto_anterior:
            gesto_anterior = gesto_actual
            inicio_gesto = time.monotonic()
            gesto_ejecutado = False

        if (
            gesto_actual in [
                "MANO ABIERTA",
                "INDICE LEVANTADO",
                "PUNO CERRADO"
            ]
            and not gesto_ejecutado
            and inicio_gesto is not None
            and time.monotonic() - inicio_gesto >= tiempo_gesto
        ):
            gesto_ejecutado = True

            if gesto_actual == "MANO ABIERTA":
                if combinacion_activada:
                    mensaje = "El mecanismo esta activado."
                else:
                    mensaje = "El mecanismo necesita dos objetos."

            elif gesto_actual == "INDICE LEVANTADO":
                if not mecanismo_seleccionado:
                    mecanismo_seleccionado = True
                    mensaje = "Mecanismo seleccionado."

                elif combinacion_activada and not puerta_abierta:
                    puerta_abierta = True
                    mensaje = "Puerta abierta. Escape completado."

                elif not combinacion_activada:
                    mensaje = "El mecanismo sigue bloqueado."

            elif gesto_actual == "PUNO CERRADO":
                mecanismo_seleccionado = False
                mensaje = "Seleccion cancelada."

        # 4. Dibujar habitación
        pantalla.fill(COLOR_FONDO)

        pygame.draw.rect(
            pantalla,
            COLOR_PARED,
            (80, 80, 840, 420)
        )

        if puerta_abierta:
            color_puerta = (25, 25, 35)
        else:
            color_puerta = (90, 75, 65)

        pygame.draw.rect(
            pantalla,
            color_puerta,
            (440, 260, 120, 240)
        )

        # 5. Indicador del mecanismo
        color_mecanismo = (
            (90, 200, 120)
            if combinacion_activada
            else (150, 65, 65)
        )

        pygame.draw.circle(
            pantalla,
            color_mecanismo,
            (500, 300),
            15
        )

        # Barra de progreso
        if not combinacion_activada and progreso_combinacion > 0:

            pygame.draw.rect(
                pantalla,
                (75, 75, 85),
                (370, 465, 260, 15)
            )

            pygame.draw.rect(
                pantalla,
                (90, 200, 120),
                (
                    370,
                    465,
                    int(260 * progreso_combinacion),
                    15
                )
            )

        # Mensaje de mecanismo activado
        if combinacion_activada:

            texto_exito = fuente_pequena.render(
                "MECANISMO ACTIVADO",
                True,
                COLOR_VALIDO
            )

            pantalla.blit(texto_exito, (385, 225))

        # Dibujar cajon
        color_cajon = (
            (130, 105, 80)
            if cajon_abierto
            else (95, 70, 55)
        )

        pygame.draw.rect(
            pantalla,
            color_cajon,
            cajon
        )

        texto_cajon = fuente_pequena.render(
            "CAJON ABIERTO" if cajon_abierto else "CAJON",
            True,
            COLOR_TEXTO
        )

        pantalla.blit(
            texto_cajon,
            (cajon.x + 8, cajon.y + 20)
        )
        
        # 6. Dibujar objetos
        for objeto in objetos:

            if (
                not objeto["recogido"]
                and (
                    objeto["nombre"] != "Llave"
                    or cajon_abierto
                )
            ):

                pygame.draw.rect(
                    pantalla,
                    COLOR_OBJETO,
                    objeto["rect"]
                )

                etiqueta = fuente_pequena.render(
                    objeto["nombre"],
                    True,
                    COLOR_TEXTO
                )

                pantalla.blit(
                    etiqueta,
                    (
                        objeto["rect"].x,
                        objeto["rect"].y - 25
                    )
                )

        # 7. Mensaje principal
        texto_mensaje = fuente_pequena.render(
            mensaje,
            True,
            COLOR_TEXTO
        )

        pantalla.blit(texto_mensaje, (80, 30))

        # 8. Inventario
        pygame.draw.rect(
            pantalla,
            COLOR_INVENTARIO,
            (0, 530, ANCHO, 120)
        )

        titulo = fuente.render(
            "INVENTARIO",
            True,
            COLOR_TEXTO
        )

        pantalla.blit(titulo, (30, 545))

        for i, nombre in enumerate(inventario):

            color = (
                COLOR_VALIDO
                if nombre == objeto_detectado
                else COLOR_TEXTO
            )

            texto = fuente_pequena.render(
                nombre,
                True,
                color
            )

            pantalla.blit(
                texto,
                (40 + i * 150, 595)
            )

        # Mostrar gesto reconocido
        texto_gesto = fuente_pequena.render(
            f"Gesto: {gesto_actual}",
            True,
            COLOR_TEXTO
        )

        pantalla.blit(texto_gesto, (610, 480))

        # 9. Mostrar tarjeta reconocida
        if objeto_detectado is not None:

            texto = fuente_pequena.render(
                f"Tarjeta reconocida: {objeto_detectado}",
                True,
                COLOR_VALIDO
            )

            pantalla.blit(texto, (610, 510))

        # 10. Vista previa de la cámara
        if imagen_camara is not None:

            imagen_rgb = cv2.cvtColor(
                imagen_camara,
                cv2.COLOR_BGR2RGB
            )

            imagen_rgb = cv2.resize(
                imagen_rgb,
                (240, 180)
            )

            superficie_camara = pygame.image.frombuffer(
                imagen_rgb.tobytes(),
                (240, 180),
                "RGB"
            )

            pantalla.blit(
                superficie_camara,
                (680, 90)
            )

        # Actualizar pantalla
        pygame.display.flip()
        reloj.tick(30)

finally:
    lector.cerrar()
    lector_gestos.cerrar()
    pygame.quit()
