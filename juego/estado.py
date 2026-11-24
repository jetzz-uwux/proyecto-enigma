class EstadoJuego:
    def __init__(self):
        self.cajon_abierto = False
        self.llave_obtenida = False
        self.nota_obtenida = False
        self.reloj_resuelto = False
        self.baul_abierto = False
        self.palabra_validada = False
        self.tarjeta_obtenida = False
        self.acceso_autorizado = False
        self.puerta_abierta = False
        self.juego_completado = False

    def resolver_reloj(self):
        if not self.nota_obtenida:
            return False
        self.reloj_resuelto = True
        return True

    def validar_palabra(self, texto):
        import unicodedata
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto.casefold()) if not unicodedata.combining(c)).strip()
        if self.baul_abierto and self.reloj_resuelto and texto == 'telon':
            self.palabra_validada = True
            return True
        return False

    def confirmar_salida(self):
        if not self.acceso_autorizado:
            return False
        self.puerta_abierta = True
        self.juego_completado = True
        return True
