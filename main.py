import flet as ft
import asyncio
import cv2
import base64
import requests
import numpy as np
import time
import serial
import atexit
from pyzbar.pyzbar import decode, ZBarSymbol
import threading
from components.buttonObi import buttonObi
from components.monitor_mesa import MonitorMesa
from components.api import payloadsApi
from components.secrets import TokenApi, urlApi 

# Variables globales
escaneando_qr = False
monitor_paused = False  # Controlamos si el monitor está en pausa actualizandose
accion_en_progreso = {}  # Diccionario para las mesas en acción
stop_event = None  # Variable para detener el hilo de la cámara

# Configura el puerto serial y la velocidad del puerto al inicio del programa
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Espera para que se establezca la conexión y el Arduino se reinicie

def main(page: ft.Page):
    global escaneando_qr, monitor_paused, stop_event
    page.adaptive = True
    page.window_always_on_top = True
    page.window_width = 1024
    page.window_height = 600
    page.window_resizable = True
    page.window_full_screen = True

    button_refs = {}
    splash_screen_visible = True
    dlg_modal = None  # Modal activo
    current_button_id = None

    # Cerrar recursos cuando se cierra la ventana de la aplicación
    def on_close(e):
        close_resources()
        print("Aplicación cerrada.")

    page.on_window_close = on_close

    def hide_splash():
        nonlocal splash_screen_visible
        splash_screen_visible = False
        page.splash = None        
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text("Mesas de trabajo")
    )
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.TABLE_RESTAURANT, label="Espacios"),
            ft.NavigationDestination(icon=ft.icons.CALENDAR_MONTH_OUTLINED, label="Calendario"),
            ft.NavigationDestination(
                icon=ft.icons.BOOKMARK_BORDER,
                selected_icon=ft.icons.BOOKMARK,
                label="Bookmark",
            ),
        ],
        border=ft.Border(
            top=ft.BorderSide(color='#052147', width=0)
        ),
        bgcolor='#1EF50A',
        on_change=print("hola")
    )

    # Función para actualizar la UI cuando se reciben los estados de las mesas
    def update_ui(mesa_id, estado):
        print(f"Actualizando UI para mesa {mesa_id} con estado {estado}")
        if mesa_id in button_refs:
            # Cambiar el color del botón en función del estado
            if estado == 1:  # Mesa ocupada
                button_refs[mesa_id].bgcolor = '#7E0315'  # Rojo para ocupado
                button_refs[mesa_id].content.controls[1].value = "Ocupado"  
            else:  # Mesa disponible
                button_refs[mesa_id].bgcolor = '#0A3C82'  # Azul para disponible
                button_refs[mesa_id].content.controls[1].value = "Disponible"   
            
            button_refs[mesa_id].update()

        if splash_screen_visible and mesa_id == num_mesas:
            hide_splash()

    def crear_teclado_numerico(campo_clave, page):
        ancho = 100
        alto = 30

        def agregar_numero(e):
            campo_clave.value += e.control.data
            campo_clave.update()

        def retroceder(e):
            campo_clave.value = campo_clave.value[:-1]
            campo_clave.update()

        fila1 = ft.Row(
            controls=[
                ft.ElevatedButton(text="1", data="1", on_click=agregar_numero, width=ancho, height=alto),
                ft.ElevatedButton(text="2", data="2", on_click=agregar_numero, width=ancho, height=alto),
                ft.ElevatedButton(text="3", data="3", on_click=agregar_numero, width=ancho, height=alto)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        fila2 = ft.Row(
            controls=[
                ft.ElevatedButton(text="4", data="4", on_click=agregar_numero, width=ancho, height=alto),
                ft.ElevatedButton(text="5", data="5", on_click=agregar_numero, width=ancho, height=alto),
                ft.ElevatedButton(text="6", data="6", on_click=agregar_numero, width=ancho, height=alto)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        fila3 = ft.Row(
            controls=[
                ft.ElevatedButton(text="7", data="7", on_click=agregar_numero, width=ancho, height=alto),
                ft.ElevatedButton(text="8", data="8", on_click=agregar_numero, width=ancho, height=alto),
                ft.ElevatedButton(text="9", data="9", on_click=agregar_numero, width=ancho, height=alto)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        fila4 = ft.Row(
            controls=[
                ft.ElevatedButton(text="0", data="0", on_click=agregar_numero, width=ancho*2, height=alto),
                ft.ElevatedButton(text="⌫", on_click=retroceder, width=ancho, height=alto),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        teclado = ft.Column(
            controls=[fila1, fila2, fila3, fila4],
            alignment=ft.MainAxisAlignment.CENTER
        )

        return teclado

    def control_mesa(mesas):
        print(f"Data: {mesas}")
        # Aquí controlamos la energia de las mesas
        try:
            arduino.write(mesas.encode())
            respuesta = arduino.readline().decode().strip()
            print(f"Respuesta del Arduino: {respuesta}")

        except serial.SerialException as e:
            print(f"Error de comunicación con el puerto serial: {e}")
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")


    num_mesas = 14
    def close_resources():
        if arduino.is_open:
            arduino.close()
            print("Puerto serial cerrado correctamente.")


    def on_button_click(e, button_id):
        print(f"Button {button_id} clicked")
        abrir_modal_clave(button_id)

    def mostrar_mensaje_confirmacion(mensaje):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje),
            action="Cerrar",
        )
        page.snack_bar.open = True
        page.update()

    def process_qr_code(matricula, page):
        global current_button_id
        if current_button_id is None:
            print("Error: button_id es None, no se puede continuar.")
            return
        
        print(f"QR escaneado con matrícula: {matricula} para mesa {current_button_id}")
        iniciar_mesa(matricula, current_button_id)  # Usamos el QR como TarjetaAlumno
        close_dlg()  # Cerrar el modal tras el escaneo

    def scan_qr(update_image, process_qr_code, page, stop_event):
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)   # Para raspberry pi

        try:
            while not stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    continue

                decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])

                for obj in decoded_objects:
                    matricula = obj.data.decode("utf-8")
                    process_qr_code(matricula, page)
                    stop_event.set()

                _, img_encoded = cv2.imencode('.jpg', frame)
                img_bytes = img_encoded.tobytes()

                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                update_image(img_base64)

        finally:
            if cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()

    def abrir_modal_clave(button_id):
        global escaneando_qr, monitor_paused, current_button_id, stop_event   
        nonlocal dlg_modal

        if monitor_paused:
            return  # Evitar abrir más modales mientras hay uno abierto

        monitor_paused = True  # Pausar el monitoreo de las mesas
        escaneando_qr = True  # Indicar que estamos escaneando QR
        current_button_id = button_id
        estado_actual = monitor.obtener_estado_mesa(button_id)
        
        def confirmar_clave(e):
            tarjeta_alumno = campo_clave.value
            if tarjeta_alumno.isdigit():
                print(f"Clave ingresada: {tarjeta_alumno}")
                if not estado_actual:
                    iniciar_mesa(tarjeta_alumno, button_id)
                else:
                    finalizar_mesa(tarjeta_alumno, button_id)
                close_dlg()   
            else:
                error_text.value = "Por favor, ingrese una clave válida."
                page.update()

        campo_clave = ft.TextField(label="Opción 2: Ingresa tu matrícula", password=False, border="underline", filled=True, keyboard_type=ft.KeyboardType.NUMBER)
        sub_text = ft.Text("Opción 1: muestre su QR", color=ft.colors.RED)

        camera_text = ft.Text("Iniciando cámara...", size=20)
        camera_image = ft.Image(width=200, height=200)

        teclado_numerico = crear_teclado_numerico(campo_clave, page)

        if estado_actual:
            titulo = f"Desbloquear Mesa {button_id}"
        else:
            titulo = f"Solicitar Mesa {button_id}"

        def update_image(img_base64):
            if dlg_modal.content.controls[0].content.controls[1] == camera_text:
                dlg_modal.content.controls[0].content.controls[1] = camera_image
            camera_image.src_base64 = img_base64
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Row([
                ft.Container(
                    content=ft.Column(
                        controls=[sub_text, camera_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=300,
                    width=300,
                ),                
                ft.Container(
                    content=ft.Column(
                        controls=[campo_clave, teclado_numerico],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=300,
                    width=400,
                )                
            ]),
            actions=[
                ft.TextButton("Confirmar", on_click=confirmar_clave),
                ft.TextButton("Cancelar", on_click=close_dlg)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        open_dlg_modal()

        stop_event = threading.Event()
        threading.Thread(target=scan_qr, args=(update_image, process_qr_code, page, stop_event), daemon=True).start()

    def close_dlg(e=None):
        global escaneando_qr, monitor_paused, stop_event
        nonlocal dlg_modal
        if dlg_modal is not None:
            dlg_modal.open = False
            escaneando_qr = False
            monitor_paused = False
            
            if stop_event is not None:
                stop_event.set()

            import time
            time.sleep(0.5)
            stop_event = None
            page.update()

    def open_dlg_modal(e=None):
        nonlocal dlg_modal
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
    
    def iniciar_mesa(tarjeta_alumno, button_id):
        global accion_en_progreso
        print(f"Iniciando mesa {button_id} con TarjetaAlumno: {tarjeta_alumno}")
        
        accion_en_progreso[button_id] = True

        payload = payloadsApi.iniciarMesaApi(TokenApi, tarjeta_alumno, button_id)
        print(f"Payload generado: {payload}")
        
        try:
            response = requests.post(urlApi, json=payload, headers=payloadsApi.headers)
            if response.status_code == 200:
                response_json = response.json()
                if response_json['Codigo'] == '1':
                    print(f"API ha confirmado que la mesa {button_id} se ha ocupado correctamente.")
                    mostrar_mensaje_confirmacion(f"Mesa {button_id} iniciada correctamente")
                    asyncio.run(monitor.consultar_estado_todas_mesas())
                else:
                    print(f"Error desconocido: {response_json['Codigo']}")
                    mostrar_mensaje_confirmacion(f"Error desconocido: {response_json['Codigo']}")
            else:
                print(f"Error en la API: {response.status_code} - {response.text}")
                mostrar_mensaje_confirmacion(f"Error al ocupar la mesa {button_id}")
        except Exception as e:
            print(f"Error enviando el payload a la API: {e}")
            mostrar_mensaje_confirmacion(f"Error en la solicitud API para mesa {button_id}")
        
        accion_en_progreso[button_id] = False

    def finalizar_mesa(tarjeta_alumno, button_id):
        global accion_en_progreso
        print(f"Finalizando mesa {button_id} con TarjetaAlumno: {tarjeta_alumno}")
        
        accion_en_progreso[button_id] = True

        payload = payloadsApi.finalizarMesaApi(TokenApi, tarjeta_alumno, button_id)
        print(f"Payload generado: {payload}")
        
        try:
            response = requests.post(urlApi, json=payload, headers=payloadsApi.headers)
            if response.status_code == 200:
                response_json = response.json()
                if response_json['Codigo'] == '1':
                    print(f"API ha confirmado que la mesa {button_id} se ha finalizado correctamente.")
                    mostrar_mensaje_confirmacion(f"Mesa {button_id} desocupada correctamente")
                    asyncio.run(monitor.consultar_estado_todas_mesas())
                else:
                    print(f"Error desconocido: {response_json['Codigo']}")
                    mostrar_mensaje_confirmacion(f"Error desconocido: {response_json['Codigo']}")
            else:
                print(f"Error en la API: {response.status_code} - {response.text}")
                mostrar_mensaje_confirmacion(f"Error al desocupar la mesa {button_id}")
        except Exception as e:
            print(f"Error enviando el payload a la API: {e}")
            mostrar_mensaje_confirmacion(f"Error en la solicitud API para mesa {button_id}")
        
        accion_en_progreso[button_id] = False

    def crear_fila_botones(start_id, cantidad):
        fila_botones = []
        for i in range(start_id, start_id + cantidad):
            boton = buttonObi(button_id=i, on_click=on_button_click).obtener_boton()
            button_refs[i] = boton
            fila_botones.append(boton)
        return ft.Row(controls=fila_botones, alignment=ft.MainAxisAlignment.END)

    page.add(
        ft.SafeArea(
            ft.Row([
                ft.Container(
                    content=ft.Column(
                        controls=[
                            crear_fila_botones(1, 3),
                            crear_fila_botones(4, 4),
                            crear_fila_botones(8, 5),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=400,
                    width=770,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            buttonObi(button_id=13, on_click=on_button_click).obtener_boton(),
                            buttonObi(button_id=14, on_click=on_button_click).obtener_boton()
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=400,
                    width=205,
                ),
            ]),
        )
    )

    page.update()

    monitor = MonitorMesa(num_mesas, update_ui, control_mesa)

    def iniciar_monitor():
        asyncio.run(monitor.monitor_estado_mesas())

    threading.Thread(target=iniciar_monitor, daemon=True).start()
    atexit.register(close_resources)

ft.app(target=main)
