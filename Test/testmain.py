import flet as ft
import serial
import time

# Configurar el puerto serial (ajusta el puerto y la velocidad según sea necesario)
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Cambia '/dev/ttyUSB0' por el puerto serial correspondiente

def main(page: ft.Page):
    def enviar_datos(e):
        # Enviar '1'
        ser.write(b'1\n')
        print("Enviado: 1")
        time.sleep(1)  # Esperar 1 segundo
        # Enviar '0'
        ser.write(b'0\n')
        print("Enviado: 0")

    page.add(ft.ElevatedButton(text="Enviar datos", on_click=enviar_datos))

ft.app(target=main)
