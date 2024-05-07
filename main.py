import flet as ft
from flet import Column, Container, Page, Row, Text, colors, icons
from components.secrets import TokenApi, urlApi
from components.api import payloadsApi
from datetime import datetime
#from raspberrypi4.lector import lecturaDeTarjeta
import threading
import requests
import json

def main(page: Page):
    page.adaptive = True
    page.window_always_on_top = True
    page.window_width = 1024
    page.window_height = 600
    page.window_resizable = False
    page.window_full_screen = False
    
    
    dlg_modal = None
    button_refs = {}
    button_id = None
    color_ocupado = '#7E0315' #7E0315 = Rojo
    color_disponible = '#0A3C82'    #0A3C82  = Azul

    page.splash = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src=f"assets/logosup.png",
                            width=500,
                            height=150,
                            fit=ft.ImageFit.CONTAIN,
                            border_radius=ft.border_radius.all(10)
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(width=50, height=50),
                    ],
                    alignment = ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src=f"assets/logo_eium.png",
                            width=150,
                            height=150,
                            fit=ft.ImageFit.CONTAIN,
                            border_radius=ft.border_radius.all(10)
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),

        ],
        alignment = ft.MainAxisAlignment.CENTER,),
        alignment = ft.alignment.center
    )
    page.update()
    
    page.appbar = ft.AppBar(
        title=ft.Text("Mesas de trabajo"),
        bgcolor=colors.with_opacity(0.1, ft.cupertino_colors.SYSTEM_BACKGROUND),
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
        bgcolor = '#1EF50A',
        on_change=print("hola")
        #overlay_color ="#1EF50A2",
    )

    print("Creando lista de usuarios vacía...")
    # Crear lista vacía y sobrescribir el archivo existente
    usuarios_activos = []
    with open('components/usuarios_activos.json', 'w') as archivo:
        json.dump(usuarios_activos, archivo)
    print("Lista de usuarios reiniciada")


    def estado_ocupado(button_id):
        estado = ft.Column([ft.Text(value=f"Mesa {button_id}", size=15, color=ft.colors.WHITE),
                                ft.Text(value=f"Ocupado", size=10, color=ft.colors.WHITE),],alignment=ft.MainAxisAlignment.CENTER,)
        return estado

    def estado_disponible(button_id):
        estado = ft.Column([ft.Text(value=f"Mesa {button_id}", size=15, color=ft.colors.WHITE),
                                ft.Text(value=f"Disponible", size=10, color=ft.colors.WHITE),],alignment=ft.MainAxisAlignment.CENTER,)
        return estado
    
    def cargar_usuarios_activos():
        global usuarios_activos
        try:
            with open('components/usuarios_activos.json', 'r') as archivo:
                usuarios_activos = json.load(archivo)
        except FileNotFoundError:
            usuarios_activos = []

    def guardar_usuario_activo(mesa_id,user_id,FechaHora_Inicio,Estado):
        if not mesa_id or not user_id or not FechaHora_Inicio:
            raise ValueError("Datos insuficientes para guardar el usuario activo.")

        usuario = {
            'id': mesa_id,
            'matricula': user_id,
            'hora_inicio': FechaHora_Inicio,
            'estado_mesa': Estado
        }
        usuarios_activos.append(usuario)
        with open('components/usuarios_activos.json', 'w') as archivo:
            json.dump(usuarios_activos, archivo)
        cargar_usuarios_activos()

    def eliminar_usuario_activo(user_id):
        global usuarios_activos
        usuarios_activos = [usuario for usuario in usuarios_activos if usuario["matricula"] != str(user_id)]
        with open('components/usuarios_activos.json', 'w') as archivo:
            json.dump(usuarios_activos, archivo)
        cargar_usuarios_activos()

    def consultar_id(button_id, estadoMesa):
        # Cierra el diálogo actual
        close_dlg()
        
        solicitarEscanear(button_id, estadoMesa)        
        print("Button ID:", button_id)

    def close_dlg(e=None):
        if dlg_modal is not None:
            dlg_modal.open = False
            page.update()

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def solicitudMesa(button_id, estadoMesa):
        nonlocal dlg_modal
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Ocupar mesa {button_id}",size=30,text_align=ft.TextAlign.CENTER),
            icon = ft.Icon(name=ft.icons.TABLE_RESTAURANT, color=ft.colors.GREEN_400, size=40),
            content=ft.Text("¿Confirmar acción?",size=25,text_align=ft.TextAlign.CENTER),
            actions=[
                ft.IconButton(icon=ft.icons.CHECK_CIRCLE,
                    icon_color=ft.colors.GREEN_400,
                    icon_size=50,
                    tooltip="Aceptar",
                    on_click=lambda e: consultar_id(button_id, estadoMesa)),
                ft.IconButton(icon=ft.icons.CANCEL,
                    icon_color=ft.colors.RED_400,
                    icon_size=50,
                    tooltip="Cancelar",
                    on_click=close_dlg)
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: print("Acción cancelada"),
        )
        return dlg_modal

    def desocuparMesa(button_id, estadoMesa):
        nonlocal dlg_modal
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Desocupar mesa {button_id}",size=30,text_align=ft.TextAlign.CENTER),
            icon = ft.Icon(name=ft.icons.TABLE_RESTAURANT, color=ft.colors.GREEN_400, size=40),
            content=ft.Text("¿Confirmar acción?",size=25,text_align=ft.TextAlign.CENTER),
            actions=[
                ft.IconButton(icon=ft.icons.CHECK_CIRCLE,
                    icon_color=ft.colors.GREEN_400,
                    icon_size=50,
                    tooltip="Aceptar",
                    on_click=lambda e: consultar_id(button_id, estadoMesa)),
                ft.IconButton(icon=ft.icons.CANCEL,
                    icon_color=ft.colors.RED_400,
                    icon_size=50,
                    tooltip="Cancelar",
                    on_click=close_dlg)
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: print("Acción cancelada"),
        )
        return dlg_modal
    
    def solicitarEscanear(button_id, estadoMesa):
        nonlocal dlg_modal
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Por favor acerque su credencial al lector", size=25, text_align=ft.TextAlign.CENTER),
            icon=ft.Icon(name=ft.icons.SIGNAL_WIFI_4_BAR, color=ft.colors.GREEN_400, size=40),
            content=ft.Text("Esperando lectura...", size=25, text_align=ft.TextAlign.CENTER),
            actions=[
                ft.IconButton(icon=ft.icons.CANCEL,
                            icon_color=ft.colors.RED_400,
                            icon_size=50,
                            tooltip="Cancelar",
                            on_click=close_dlg)
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: print("Acción cancelada"),
        )
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
        threading.Timer(1, check_rfid_response, args=[button_id,estadoMesa]).start()   
    
    def comprobar_usuario_activo(user_id):
        # Verificar si el id ya está activo en la lista de diccionarios
        global usuarios_activos
        for usuario in usuarios_activos:
            if str(usuario['matricula']) == user_id:
                raise ValueError("Ya tienes una mesa activa")
    
    def comprobar_mesa_activa(button_id):
        # Verificar si el id ya está activo en la lista de diccionarios
        global usuarios_activos
        for mesa in usuarios_activos:
            if str(mesa['id']) == str(button_id):
                return mesa['estado_mesa']
    
    def comprobar_vinculacion_mesa(button_id, response_data, usuarios_activos, rfid_data, user_id):
        print(user_id)        
        for mesa in usuarios_activos:
            print(mesa['id'])
            print(str(button_id))
            print(mesa['matricula'])
            print(str(user_id))
            if str(mesa['id']) == str(button_id) and mesa['matricula'] == str(user_id):
                print("si entra")
                incidencia = 1
                response = requests.post(urlApi,json=payloadsApi.finalizarMesaApi(TokenApi,rfid_data, button_id))
                if response.status_code == 200:
                    response_data = response.json()
                    print(response_data)
                    if response_data['Codigo'] == '1':                           
                        dlg_modal.title=ft.Text(f"Acceso autorizado:", size=25, text_align=ft.TextAlign.CENTER)
                        dlg_modal.content = ft.Text(f"{response_data['Mensaje']}", size=25, text_align=ft.TextAlign.CENTER)
                        eliminar_usuario_activo(str(user_id))
                        if button_id in button_refs:
                            button_refs[button_id].bgcolor = color_disponible  # Cambia a azul                            
                            button_refs[button_id].content = estado_disponible(button_id)
                            page.update()
                            return                        
                    raise ValueError((f"{response_data['Mensaje']}"))                




    def check_rfid_response(button_id,estadoMesa):
        rfid_data = 15136485
        cargar_usuarios_activos()
        try:
            # Intenta leer el RFID
            #rfid_data = lecturaDeTarjeta()  # Simula la lectura del RFID                     
            print(usuarios_activos)
            dlg_modal.title=ft.Text(f"Leido", size=25, text_align=ft.TextAlign.CENTER)
            dlg_modal.content = ft.Text(f"Consultando {str(rfid_data)}", size=25, text_align=ft.TextAlign.CENTER)
            page.update()
            response = requests.post(urlApi,json=payloadsApi.informacionUsuarioApi(TokenApi,rfid_data,button_id))
                       
            if response.status_code == 200:
                response_data = response.json()
                user_id = str(response_data['id']) 
                print(response_data)
                if estadoMesa is not None:                    
                    comprobar_vinculacion_mesa(button_id, response_data, usuarios_activos, rfid_data, user_id) #reviso si es dueño de la mesa                
                    return
                comprobar_usuario_activo(user_id)  #reviso si ya tiene mesa activa                
                if rfid_data:
                    #print(rfid_data)
                    url = urlApi                
                    response = requests.post(urlApi, json=payloadsApi.iniciarMesaApi(TokenApi,rfid_data,button_id), headers=payloadsApi.headers)
                    
                    if response.status_code == 200:
                        # Procesa la respuesta de la API
                        response_data = response.json()
                        print(response_data)
                        
                        if response_data['Codigo'] == '1':
                            # actualizo la interfaz dependiendo de la respuesta
                            print("autorizado")
                            dlg_modal.title=ft.Text(f"Acceso autorizado:", size=25, text_align=ft.TextAlign.CENTER)
                            dlg_modal.content = ft.Text(f"{response_data['Mensaje']}", size=25, text_align=ft.TextAlign.CENTER)
                            FechaHora_Inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            guardar_usuario_activo(button_id, user_id, FechaHora_Inicio, 1)  #mesa_id,user_id,FechaHora_Inicio,Estado
                            if button_id in button_refs:
                                button_refs[button_id].bgcolor = color_ocupado  # Cambia a rojo para mostrar ocupado                            
                                button_refs[button_id].content = estado_ocupado(button_id)
                                page.update()                        
                        if response_data['Codigo'] == '0':
                            print("denegado")
                            dlg_modal.title=ft.Text(f"Acceso denegado:", size=25, text_align=ft.TextAlign.CENTER)
                            dlg_modal.content = ft.Text(f"{response_data['Mensaje']}", size=25, text_align=ft.TextAlign.CENTER)
                    else:
                        dlg_modal.content = ft.Text("Error en la respuesta de la API", size=25, text_align=ft.TextAlign.CENTER)
                else:
                    raise ValueError("No se recibió dato de RFID")
        except Exception as e:
            dlg_modal.content = ft.Text(str(e), size=25, text_align=ft.TextAlign.CENTER)
        finally:
            page.update()
            threading.Timer(2, close_dlg).start()
    

    def handle_button_click(e, button_id):        
        print(f"Button {button_id} was pressed")
        #aqui elijo si la mesa está ocupada o desocupada
        estadoMesa = comprobar_mesa_activa(button_id)
        print(estadoMesa)
        if estadoMesa is not None:
            dlg_modal = desocuparMesa(button_id, estadoMesa)
        else:
            dlg_modal = solicitudMesa(button_id, estadoMesa)
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def EspacioButton(button_id, texto, subtexto, on_click):
        button_id = button_id
        url = urlApi
        bgcolor = ''
        response = requests.post(url, json=payloadsApi.informacionApi(TokenApi,button_id), headers=payloadsApi.headers)        

        if response.status_code == 200:
            # Procesa la respuesta de la API
            response_data = response.json()
            print(response_data)
            
            if response_data['Estado'] == 0:
                bgcolor = color_disponible
                estado = estado_disponible(button_id)
            else:
                bgcolor = color_ocupado
                estado = estado_ocupado(button_id)
            if response_data['user_id'] is not None:
                mesa_id = response_data['id']
                user_id = response_data['user_id']
                FechaHora_Inicio = response_data['FechaHora_Inicio']
                Estado = response_data['Estado']
                guardar_usuario_activo(mesa_id,user_id,FechaHora_Inicio,Estado)


        btn = ft.Container(
            content=estado,
            alignment=ft.alignment.center,
            bgcolor=bgcolor,  # Color inicial
            height=115,
            width=135,
            border_radius=10,
            ink=True,
            on_click=lambda e: on_click(e, button_id),
        )
        button_refs[button_id] = btn  # Guardar referencia
        return btn

    def createRowOfButtons(buttons, start_id=1):
        return ft.Row(
            controls=[
                EspacioButton(button_id, text, status, lambda e, button_id=button_id: handle_button_click(e, button_id))
                for button_id, (text, status) in enumerate(buttons, start=start_id)
            ],
            alignment=ft.MainAxisAlignment.END
        )



    page.add(
        ft.SafeArea(
            ft.Row([
                ft.Container(
                    content=ft.Column(
                        controls=[
                            createRowOfButtons([("Mesa 1", "Disponible"), ("Mesa 2", "Disponible"), ("Mesa 3", "Disponible")], start_id=1),
                            createRowOfButtons([("Mesa 4", "Disponible"), ("Mesa 5", "Disponible"), ("Mesa 6", "Disponible"), ("Mesa 7", "Disponible")], start_id=4),
                            createRowOfButtons([("Mesa 8", "Disponible"), ("Mesa 9", "Disponible"), ("Mesa 10", "Disponible"), ("Mesa 11", "Disponible"), ("Mesa 12", "Disponible")], start_id=8),
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
                            ft.Column(
                                controls=[
                                    EspacioButton(13, "Soldadura 1", "Disponible", handle_button_click),
                                    EspacioButton(14, "Soldadura 2", "Disponible", handle_button_click),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            )
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
    page.splash = None    
    page.update()

ft.app(target=main)
