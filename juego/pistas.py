"""Pistas progresivas, independientes del reconocimiento de voz."""

def obtener_pista(estado):
    if not (estado.llave_obtenida and estado.nota_obtenida):
        return 'frontal', 'cajon', 'Revisa el cajón del tocador; aún quedan objetos por recoger.'
    if 'manecilla_hora' not in estado.manecillas_encontradas:
        return 'izquierda', 'manecilla_hora', 'Busca entre los libros de la estantería.'
    if 'manecilla_minuto' not in estado.manecillas_encontradas:
        return 'derecha', 'manecilla_minuto', 'Busca cerca de las máscaras del vestuario.'
    if len(estado.manecillas_colocadas) != 2:
        return 'izquierda', 'reloj', 'Presenta los marcadores de ambas manecillas frente al reloj.'
    if not estado.reloj_resuelto:
        return 'izquierda', 'reloj', 'Consulta la nota del inventario y observa el reloj.'
    if not estado.baul_abierto:
        return 'posterior', 'baul_cerrado', 'Selecciona la llave del inventario y revisa la cerradura del baúl.'
    if not estado.palabra_validada:
        return 'posterior', 'baul_abierto', 'Recuerda la palabra revelada por el reloj y usa el micrófono del baúl.'
    if not estado.tarjeta_obtenida:
        return 'posterior', 'tarjeta', 'Recoge la tarjeta que apareció dentro del baúl.'
    if not estado.acceso_autorizado:
        return 'posterior', 'escaner', 'Acerca la tarjeta física al escáner de la puerta.'
    if not estado.juego_completado:
        return 'posterior', 'puerta', 'Consulta la inscripción de la tarjeta con su marcador. Un dedo primero, cinco después.'
    return None, None, 'Has completado el camerino.'

def mensaje_pista(estado, vista):
    destino, _, mensaje = obtener_pista(estado)
    orden = ['frontal', 'derecha', 'posterior', 'izquierda']
    if destino and destino != vista:
        distancia = (orden.index(destino) - orden.index(vista)) % 4
        mensaje += ' Gira ' + ('a la izquierda.' if distancia == 3 else 'a la derecha.' if distancia == 1 else 'dos veces.')
    return mensaje
