class SecuenciaFinal:
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.paso = 0
        self.desde = None
        self.limite = None

    def actualizar(self, gesto, ahora):
        if self.paso == 1 and ahora > self.limite:
            self.reiniciar()
            return 'reinicio'
        esperado = 'INDICE LEVANTADO' if self.paso == 0 else 'MANO ABIERTA'
        if gesto != esperado:
            self.desde = None
            if self.paso == 1 and gesto == 'PUNO CERRADO':
                self.reiniciar()
                return 'reinicio'
            return None
        if self.desde is None:
            self.desde = ahora
        if ahora - self.desde < (0.35 if self.paso == 0 else 1.0):
            return None
        self.desde = None
        if self.paso == 0:
            self.paso = 1
            self.limite = ahora + 8.0
            return 'primero'
        self.reiniciar()
        return 'completo'
