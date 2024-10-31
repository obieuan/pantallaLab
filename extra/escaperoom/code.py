import flet as ft
import RPi.GPIO as GPIO
import threading
import time

def main(page: ft.Page):
    page.title = "Sci-Fi Code Display"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK
    page.update()
    
    # Crear el texto que mostrará el código
    code_text = ft.Text(
        "",
        size=100,
        color=ft.colors.LIME_ACCENT_400,
        font_family="Consolas",
        weight=ft.FontWeight.BOLD,
    )
    
    # Crear un contenedor con estilo sci-fi
    container = ft.Container(
        content=code_text,
        alignment=ft.alignment.center,
        bgcolor=ft.colors.BLACK,
        padding=20,
        border_radius=10,
        border=ft.border.all(2, ft.colors.LIME_ACCENT_400),
        shadow=ft.BoxShadow(
            spread_radius=5,
            blur_radius=15,
            color=ft.colors.LIME_ACCENT_400,
            offset=ft.Offset(0, 0),
        ),
    )
    page.add(container)
    
    # Configuración del GPIO
    GPIO.setmode(GPIO.BCM)  # Usar numeración BCM

    # Pin para el botón
    GPIO_BUTTON_PIN = 17  # Por ejemplo, GPIO17
    GPIO.setup(GPIO_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Pin para el relé
    GPIO_RELAY_PIN = 27  # Por ejemplo, GPIO27
    GPIO.setup(GPIO_RELAY_PIN, GPIO.OUT)
    GPIO.output(GPIO_RELAY_PIN, GPIO.LOW)  # Asegurar que el relé esté inicialmente apagado
    
    # Función para monitorear el GPIO
    def monitor_gpio():
        while True:
            if GPIO.input(GPIO_BUTTON_PIN) == GPIO.HIGH:
                # Cuando se presiona el botón, actualizar la interfaz y activar el relé
                page.call_from_thread(display_code_and_activate_relay)
                time.sleep(0.5)  # Retardo para evitar rebotes
            time.sleep(0.1)  # Intervalo de sondeo
    
    def display_code_and_activate_relay():
        code_text.value = "335875"
        code_text.update()
        GPIO.output(GPIO_RELAY_PIN, GPIO.HIGH)  # Activar el relé
        # Si deseas que el relé se desactive después de un tiempo, puedes usar un temporizador
        threading.Timer(5, deactivate_relay).start()  # Desactiva el relé después de 5 segundos

    def deactivate_relay():
        GPIO.output(GPIO_RELAY_PIN, GPIO.LOW)  # Desactivar el relé

    # Iniciar el hilo que monitorea el GPIO
    gpio_thread = threading.Thread(target=monitor_gpio, daemon=True)
    gpio_thread.start()
    
    # Ejecutar la aplicación
    page.update()

ft.app(target=main)
