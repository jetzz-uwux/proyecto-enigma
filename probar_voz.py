import time
from interacciones.voz import ReconocedorVoz


def main():
    print("Cargando modelo de voz...")
    voz = ReconocedorVoz()
    print("Modelo listo.\n")

    try:
        while True:
            entrada = input("Presiona ENTER para escuchar (o escribe 'salir'): ").strip().lower()
            if entrada == "salir":
                break

            print("🎙️ Escuchando... di 'TELÓN', 'pista' o una palabra incorrecta.")
            voz.escuchar(tiempo_max=4)

            # Simulación de bucle principal de Pygame (no bloqueante)
            while voz.esta_escuchando():
                comando = voz.obtener_comando()
                if comando is not None:
                    print(f"-> Resultado detectado: {comando}")
                    break
                time.sleep(0.05)

            # Recoge el resultado final si terminó justo al salir del bucle
            comando_final = voz.obtener_comando()
            if comando_final is not None:
                print(f"-> Resultado detectado: {comando_final}")

            # Verificación de que el resultado se limpió correctamente
            print(f"-> Lectura posterior (debe ser None): {voz.obtener_comando()}\n")

    finally:
        voz.cerrar()
        print("Reconocedor cerrado correctamente.")


if __name__ == "__main__":
    main()