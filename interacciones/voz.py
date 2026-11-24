import json
import os
import queue
import threading
import time
import unicodedata

import sounddevice as sd
from vosk import KaldiRecognizer, Model, SetLogLevel


class ReconocedorVoz:
    def __init__(self, ruta_modelo="modelos/vosk-model-small-es-0.42", sample_rate=16000):
        # Silencia los logs internos de Vosk en la consola
        SetLogLevel(-1)

        if not os.path.exists(ruta_modelo):
            raise FileNotFoundError(
                f"No se encontró el modelo de Vosk en: {os.path.abspath(ruta_modelo)}"
            )

        self.sample_rate = sample_rate
        self.modelo = Model(ruta_modelo)

        # Gramática restringida: fuerza a Vosk a buscar solo estas palabras o [unk] (desconocido)
        self.gramatica = json.dumps(["telón", "telon", "pista", "[unk]"], ensure_ascii=False)

        self._lock = threading.Lock()
        self._escuchando = False
        self._detener_evento = threading.Event()
        self._comando_pendiente = None
        self._hilo = None

    @staticmethod
    def _normalizar(texto):
        """Convierte a minúsculas y elimina tildes."""
        texto = texto.lower().strip()
        return "".join(
            c for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn"
        )

    def _extraer_comando(self, texto):
        """Busca si el texto contiene alguna de las palabras clave válidas."""
        limpio = self._normalizar(texto)
        palabras = limpio.split()
        if "telon" in palabras:
            return "TELON"
        if "pista" in palabras:
            return "PISTA"
        return None

    def escuchar(self, tiempo_max=4):
        """Inicia la escucha en segundo plano si el micrófono no está activo."""
        with self._lock:
            if self._escuchando:
                return
            self._escuchando = True
            self._comando_pendiente = None
            self._detener_evento.clear()

        self._hilo = threading.Thread(
            target=self._proceso_escucha,
            args=(tiempo_max,),
            daemon=True,
        )
        self._hilo.start()

    def _proceso_escucha(self, tiempo_max):
        cola_audio = queue.Queue()
        reconocedor = KaldiRecognizer(self.modelo, self.sample_rate, self.gramatica)
        resultado_final = "INCORRECTO"

        def callback_audio(indata, frames, time_info, status):
            if not self._detener_evento.is_set():
                cola_audio.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=4000,
                dtype="int16",
                channels=1,
                callback=callback_audio,
            ):
                tiempo_limite = time.monotonic() + tiempo_max

                while time.monotonic() < tiempo_limite and not self._detener_evento.is_set():
                    try:
                        datos = cola_audio.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    if reconocedor.AcceptWaveform(datos):
                        res = json.loads(reconocedor.Result())
                        comando = self._extraer_comando(res.get("text", ""))
                        if comando:
                            resultado_final = comando
                            break
                    else:
                        parcial = json.loads(reconocedor.PartialResult())
                        comando = self._extraer_comando(parcial.get("partial", ""))
                        if comando:
                            resultado_final = comando
                            break

                # Revisa el último fragmento capturado antes de cerrar
                if resultado_final == "INCORRECTO" and not self._detener_evento.is_set():
                    res_final = json.loads(reconocedor.FinalResult())
                    comando = self._extraer_comando(res_final.get("text", ""))
                    if comando:
                        resultado_final = comando

        except Exception as e:
            print(f"[ReconocedorVoz] Error de micrófono: {e}")
            resultado_final = "INCORRECTO"

        finally:
            with self._lock:
                # Solo guarda el resultado si no se mandó a cerrar el módulo
                if not self._detener_evento.is_set():
                    self._comando_pendiente = resultado_final
                self._escuchando = False

    def obtener_comando(self):
        """Devuelve el comando detectado una sola vez y lo limpia."""
        with self._lock:
            comando = self._comando_pendiente
            self._comando_pendiente = None
            return comando

    def esta_escuchando(self):
        """Indica si el micrófono está activo actualmente."""
        with self._lock:
            return self._escuchando

    def cerrar(self):
        """Detiene cualquier escucha activa y libera el hilo de forma segura."""
        self._detener_evento.set()
        if self._hilo and self._hilo.is_alive():
            self._hilo.join(timeout=1.0)
        with self._lock:
            self._escuchando = False
            self._comando_pendiente = None