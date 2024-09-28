import flet as ft
import asyncio
import cv2
import base64
import requests
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
import threading
from components.buttonObi import buttonObi
from components.monitor_mesa import MonitorMesa
from components.api import payloadsApi
from components.secrets import TokenApi, urlApi 

# Variable global para controlar el escaneo y el monitor
escaneando_qr = False
monitor_paused = False  # Controlamos si el monitor está en pausa actualizandose
accion_en_progreso = {}  # Diccionario para las mesas en acción


def main(page: ft.Page):
    global escaneando_qr, monitor_paused  
    page.adaptive = True
    page.window_always_on_top = True
    page.window_width = 1024
    page.window_height = 600
    page.window_resizable = False
    page.window_full_screen = False

    button_refs = {}
    splash_screen_visible = True
    dlg_modal = None  # Modal activo
    current_button_id = None  

    def hide_splash():
        nonlocal splash_screen_visible
        splash_screen_visible = False
        page.splash = None
        page.update()

    # Splash screen 
    page.splash = ft.Container(
        bgcolor=ft.colors.WHITE,
        content=ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src="assets/logosup.png",
                            width=500,
                            height=150,
                            fit=ft.ImageFit.CONTAIN,
                            border_radius=ft.border_radius.all(10)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
            ft.Container(
                content=ft.Row(
                    controls=[ft.ProgressRing(width=50, height=50)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src="assets/logo_eium.png",
                            width=150,
                            height=150,
                            fit=ft.ImageFit.CONTAIN,
                            border_radius=ft.border_radius.all(10)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center
    )
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

    # Funciones de control
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
        # Función que agrega un número al campo_clave
        ancho = 100
        alto = 30
        def agregar_numero(e):
            campo_clave.value += e.control.data
            campo_clave.update()

        # Función que elimina el último carácter del campo_clave
        def retroceder(e):
            campo_clave.value = campo_clave.value[:-1]
            campo_clave.update()

        # Crear los botones del 1 al 9
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
        # Fila final con el botón "0" y "⌫" (retroceso)
        fila4 = ft.Row(
            controls=[
                ft.ElevatedButton(text="0", data="0", on_click=agregar_numero, width=ancho*2, height=alto),
                ft.ElevatedButton(text="⌫", on_click=retroceder, width=ancho, height=alto),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Agrupar todas las filas en una columna
        teclado = ft.Column(
            controls=[fila1, fila2, fila3, fila4],
            alignment=ft.MainAxisAlignment.CENTER
        )

        return teclado

    def control_mesa(mesa_id, estado):
        print(f"Controlando mesa física {mesa_id} con estado {estado}")
        # Aquí controlamos la energia de las mesas

    num_mesas = 14

    # Función para manejar el clic en el botón de una mesa
    def on_button_click(e, button_id):
        print(f"Button {button_id} clicked")
        abrir_modal_clave(button_id)

    # Función para mostrar un mensaje de confirmación al usuario
    def mostrar_mensaje_confirmacion(mensaje):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje),
            action="Cerrar",
        )
        page.snack_bar.open = True
        page.update()

    # Función para procesar el QR escaneado
    def process_qr_code(matricula, page):
        global current_button_id
        if current_button_id is None:
            print("Error: button_id es None, no se puede continuar.")
            return
        
        print(f"QR escaneado con matrícula: {matricula} para mesa {current_button_id}")
        iniciar_mesa(matricula, current_button_id)  # Usamos el QR como TarjetaAlumno
        close_dlg()  # Cerrar el modal tras el escaneo

    # Función para escanear el QR y actualizar la pantalla en Flet
    def scan_qr(update_image, process_qr_code, page, stop_event):
        cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)   #Para windows
        #cap = cv2.VideoCapture(0, cv2.CAP_V4L2)   #Para raspberry pi


        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                continue

            # Decodificamos solo los códigos QR (ZBarSymbol.QRCODE filtra únicamente QR)
            decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])

            for obj in decoded_objects:
                matricula = obj.data.decode("utf-8")
                process_qr_code(matricula, page)
                stop_event.set()   

            # Convertir el frame en imagen JPEG
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = img_encoded.tobytes()

            # Convertimos la imagen en formato base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            # Actualizamos la imagen en la pantalla usando src_base64
            update_image(img_base64)

        cap.release()

    # Función para abrir el modal y mostrar la cámara o para pedir la clave
    def abrir_modal_clave(button_id):
        global escaneando_qr, monitor_paused, current_button_id   
        nonlocal dlg_modal

        if monitor_paused:
            return  # Evitar abrir más modales mientras hay uno abierto

        monitor_paused = True  # Pausar el monitoreo de las mesas
        escaneando_qr = True  # Indicar que estamos escaneando QR
        current_button_id = button_id  # Guardar el button_id actual para el escaneo de QR
        estado_actual = monitor.obtener_estado_mesa(button_id) # Guardar el estado actual del boton para saber si esta ocupado o desocupado
        

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

        # Crear el campo de entrada y el mensaje de error
        campo_clave = ft.TextField(label="Opción 2: Ingresa tu matrícula", password=False, border="underline", filled=True, keyboard_type=ft.KeyboardType.NUMBER)
        sub_text = ft.Text("Opción 1: muestre su QR", color=ft.colors.RED)

        # Placeholder de texto mientras se inicia la cámara
        camera_text = ft.Text("Iniciando cámara...", size=20)  # Texto temporal en lugar de la cámara

        # Crear un contenedor para mostrar la imagen de la cámara
        camera_image = ft.Image(width=200, height=200)

        teclado_numerico = crear_teclado_numerico(campo_clave, page)

        if estado_actual:
            titulo = f"Desbloquear Mesa {button_id}"
        else:
            titulo = f"Solicitar Mesa {button_id}"

        # Función para actualizar la imagen de la cámara en la UI
        def update_image(img_base64):
            # Si el contenido aún es el texto, lo reemplazamos por la imagen de la cámara
            if dlg_modal.content.controls[0].content.controls[1] == camera_text:
                dlg_modal.content.controls[0].content.controls[1] = camera_image  # Reemplaza el texto con la imagen de la cámara
            camera_image.src_base64 = img_base64  # Actualiza el contenido de la imagen
            page.update()

        # Crear el modal con el texto inicial
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Row([
                ft.Container(
                    content=ft.Column(
                        controls=[
                            sub_text,
                            camera_text,
                        ],
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
                        controls=[
                            campo_clave,teclado_numerico
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=300,
                    width=400,
                )                
            ]),  # Inicia con el texto de la cámara
            actions=[
                ft.TextButton("Confirmar", on_click=confirmar_clave),
                ft.TextButton("Cancelar", on_click=close_dlg)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        open_dlg_modal()  # Abre el modal

        # Iniciar el hilo de escaneo de QR
        stop_event = threading.Event()
        threading.Thread(target=scan_qr, args=(update_image, process_qr_code, page, stop_event), daemon=True).start()

    # Función para cerrar el modal
    def close_dlg(e=None):
        global escaneando_qr, monitor_paused
        nonlocal dlg_modal
        if dlg_modal is not None:
            dlg_modal.open = False
            escaneando_qr = False  # Dejamos de escanear
            monitor_paused = False  # Reanudar el monitoreo de mesas
            page.update()

    # Función para abrir el modal
    def open_dlg_modal(e=None):
        nonlocal dlg_modal
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
    
    # Función para iniciar la mesa usando la API
    def iniciar_mesa(tarjeta_alumno, button_id):
        global accion_en_progreso
        print(f"Iniciando mesa {button_id} con TarjetaAlumno: {tarjeta_alumno}")
        
        # Marcamos que la acción está en progreso para esta mesa
        accion_en_progreso[button_id] = True

        # Genera el payload usando la función iniciarMesaApi
        payload = payloadsApi.iniciarMesaApi(TokenApi, tarjeta_alumno, button_id)
        print(f"Payload generado: {payload}")
        
        # Enviar el payload a la API
        try:
            response = requests.post(urlApi, json=payload, headers=payloadsApi.headers)
            if response.status_code == 200:
                response_json = response.json()
                # Verifica el código devuelto en la respuesta JSON
                if response_json['Codigo'] == '1':
                    print(f"API ha confirmado que la mesa {button_id} se ha ocupado correctamente.")
                    mostrar_mensaje_confirmacion(f"Mesa {button_id} iniciada correctamente")
                    # Aquí llamamos al monitor para que vuelva a consultar el estado real de todas las mesas
                    asyncio.run(monitor.consultar_estado_todas_mesas())  # Llamada a la función para consultar todas las mesas
                elif response_json['Codigo'] == '1601':
                    print("Error: Parámetros no válidos. Revisa los datos enviados.")
                    mostrar_mensaje_confirmacion("Error: Parámetros no válidos.")
                elif response_json['Codigo'] == '1602':
                    print("Error: Token no válido. Notifica al administrador.")
                    mostrar_mensaje_confirmacion("Error: Token no válido.")
                elif response_json['Codigo'] == '1603':
                    print("Error: Se requiere la matrícula para este comando.")
                    mostrar_mensaje_confirmacion("Error: Matrícula no proporcionada.")
                elif response_json['Codigo'] == '1604':
                    print("Error: La matrícula no se encuentra en el sistema. Verifica la matrícula.")
                    mostrar_mensaje_confirmacion("Error: Matrícula no encontrada.")
                elif response_json['Codigo'] == '1605':
                    print("Error: El espacio no existe. Verifica el ID del espacio.")
                    mostrar_mensaje_confirmacion("Error: Espacio no encontrado.")
                elif response_json['Codigo'] == '1608':
                    print("Error: El espacio ya ha sido iniciado anteriormente.")
                    mostrar_mensaje_confirmacion("Error: El espacio ya ha sido iniciado.")
                elif response_json['Codigo'] == '1609':
                    print("Error: El alumno ya ha inicializado un espacio y sigue activo.")
                    mostrar_mensaje_confirmacion("Error: El alumno ya tiene un espacio activo.")
                else:
                    print(f"Error desconocido: {response_json['Codigo']}")
                    mostrar_mensaje_confirmacion(f"Error desconocido: {response_json['Codigo']}")
            elif response.status_code == 401:
                print("Token inválido o expirado.")
                mostrar_mensaje_confirmacion("Error: Token inválido, notifica al administrador.")            
            else:
                print(f"Error en la API: {response.status_code} - {response.text}")
                mostrar_mensaje_confirmacion(f"Error al ocupar la mesa {button_id}")
        except Exception as e:
            print(f"Error enviando el payload a la API: {e}")
            mostrar_mensaje_confirmacion(f"Error en la solicitud API para mesa {button_id}")
        
        # Una vez que la API responde, marcamos que la acción ha finalizado
        accion_en_progreso[button_id] = False


    # Función para finalizar la mesa usando la API
    def finalizar_mesa(tarjeta_alumno, button_id):
        global accion_en_progreso
        print(f"Finalizando mesa {button_id} con TarjetaAlumno: {tarjeta_alumno}")
        
        # Marcamos que la acción está en progreso para esta mesa
        accion_en_progreso[button_id] = True

        # Genera el payload usando la función finalizarMesaApi
        payload = payloadsApi.finalizarMesaApi(TokenApi, tarjeta_alumno, button_id)
        print(f"Payload generado: {payload}")
        
        # Enviar el payload a la API
        try:
            response = requests.post(urlApi, json=payload, headers=payloadsApi.headers)
            if response.status_code == 200:
                response_json = response.json()
                # Verifica el código devuelto en la respuesta JSON
                if response_json['Codigo'] == '1':
                    print(f"API ha confirmado que la mesa {button_id} se ha finalizado correctamente.")
                    mostrar_mensaje_confirmacion(f"Mesa {button_id} desocupada correctamente")
                    
                    # Aquí llamamos al monitor para que vuelva a consultar el estado real de todas las mesas
                    asyncio.run(monitor.consultar_estado_todas_mesas())  # Llamada a la función para consultar todas las mesas
                elif response_json['Codigo'] == '1601':
                    print("Error: Parámetros no válidos. Revisa los datos enviados.")
                    mostrar_mensaje_confirmacion("Error: Parámetros no válidos.")
                elif response_json['Codigo'] == '1602':
                    print("Error: Token no válido. Notifica al administrador.")
                    mostrar_mensaje_confirmacion("Error: Token no válido.")
                elif response_json['Codigo'] == '1603':
                    print("Error: Se requiere la matrícula para este comando.")
                    mostrar_mensaje_confirmacion("Error: Matrícula no proporcionada.")
                elif response_json['Codigo'] == '1604':
                    print("Error: La matrícula no se encuentra en el sistema. Verifica la matrícula.")
                elif response_json['Codigo'] == '1620':
                    print("Error: El espacio no se encuentra inicializado y no puede finalizar.")
                    mostrar_mensaje_confirmacion("Error: El espacio no ha sido iniciado.")
                elif response_json['Codigo'] == '1621':
                    print("Error: El espacio a finalizar no corresponde al usuario.")
                    mostrar_mensaje_confirmacion("Error: El espacio no corresponde a tu usuario.")
                else:
                    print(f"Error desconocido: {response_json['Codigo']}")
                    mostrar_mensaje_confirmacion(f"Error desconocido: {response_json['Codigo']}")
            elif response.status_code == 401:
                print("Token inválido o expirado. Verifica las credenciales.")
                mostrar_mensaje_confirmacion("Error: Token inválido o expirado.")
            else:
                print(f"Error en la API: {response.status_code} - {response.text}")
                mostrar_mensaje_confirmacion(f"Error al desocupar la mesa {button_id}")
        except Exception as e:
            print(f"Error enviando el payload a la API: {e}")
            mostrar_mensaje_confirmacion(f"Error en la solicitud API para mesa {button_id}")
        
        # Una vez que la API responde, marcamos que la acción ha finalizado
        accion_en_progreso[button_id] = False

    # Crear filas de botones
    def crear_fila_botones(start_id, cantidad):
        fila_botones = []
        for i in range(start_id, start_id + cantidad):
            boton = buttonObi(button_id=i, on_click=on_button_click).obtener_boton()
            button_refs[i] = boton
            fila_botones.append(boton)
        return ft.Row(controls=fila_botones, alignment=ft.MainAxisAlignment.END)

    # Añadir botones y UI
    page.add(
        ft.SafeArea(
            ft.Row([

                ft.Container(
                    content=ft.Column(
                        controls=[
                            crear_fila_botones(1, 3),  # Primera fila de botones
                            crear_fila_botones(4, 4),  # Segunda fila de botones
                            crear_fila_botones(8, 5),  # Tercera fila de botones
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

    page.update()  # Actualizar la página para agregar los botones antes del monitor

    # Crear monitor de mesas
    monitor = MonitorMesa(num_mesas, update_ui, control_mesa)

    # Aquí usamos asyncio.run para ejecutar el monitor de mesas
    def iniciar_monitor():
        asyncio.run(monitor.monitor_estado_mesas())

    # Usar un hilo separado para iniciar el bucle asyncio sin bloquear la UI
    import threading
    threading.Thread(target=iniciar_monitor, daemon=True).start()

# Ejecutar la app
ft.app(target=main)
