import flet as ft
import serial
from datetime import datetime
import json
import os

# Configurar el puerto serial (ajusta el puerto y la velocidad según sea necesario)
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Cambia '/dev/ttyUSB0' por el puerto serial correspondiente

def main(page: ft.Page):
    page.adaptive = True
    page.window_always_on_top = True
    page.window_width = 1024
    page.window_height = 600
    page.window_resizable = False
    page.window_full_screen = False
    
    dlg_modal = None
    button_refs = {}
    color_ocupado = '#7E0315'  # Rojo
    color_disponible = '#0A3C82'  # Azul
    num_mesas = 14  # Número total de mesas

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
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(width=50, height=50),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
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
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,),
        alignment=ft.alignment.center
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
        on_change=lambda _: print("hola")
    )

    def estado_ocupado(button_id):
        estado = ft.Column([ft.Text(value=f"Mesa {button_id}", size=15, color=ft.colors.WHITE),
                            ft.Text(value=f"Ocupado", size=10, color=ft.colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER)
        return estado

    def estado_disponible(button_id):
        estado = ft.Column([ft.Text(value=f"Mesa {button_id}", size=15, color=ft.colors.WHITE),
                            ft.Text(value=f"Disponible", size=10, color=ft.colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER)
        return estado
    
    def inicializar_usuarios_activos():
        global usuarios_activos
        usuarios_activos = {str(i): {"id": str(i), "hora_inicio": None, "estado_mesa": 0} for i in range(1, num_mesas + 1)}
        guardar_usuarios_activos()

    def cargar_usuarios_activos():
        global usuarios_activos
        if os.path.exists('components/usuarios_activos.json'):
            try:
                with open('components/usuarios_activos.json', 'r') as archivo:
                    usuarios_activos = json.load(archivo)
                    if not isinstance(usuarios_activos, dict):
                        inicializar_usuarios_activos()
            except (FileNotFoundError, json.JSONDecodeError):
                inicializar_usuarios_activos()
        else:
            inicializar_usuarios_activos()

    def guardar_usuarios_activos():
        global usuarios_activos
        with open('components/usuarios_activos.json', 'w') as archivo:
            json.dump(usuarios_activos, archivo)

    def actualizar_usuario_activo(mesa_id, FechaHora_Inicio, Estado):
        global usuarios_activos
        if not mesa_id or not FechaHora_Inicio:
            raise ValueError("Datos insuficientes para actualizar el usuario activo.")

        usuarios_activos[mesa_id] = {
            "id": mesa_id,
            "hora_inicio": FechaHora_Inicio,
            "estado_mesa": Estado
        }
        guardar_usuarios_activos()
        enviar_dato_serial(f"%,{mesa_id},{Estado}\n")

    def desactivar_usuario_activo(mesa_id):
        global usuarios_activos
        usuarios_activos[mesa_id] = {
            "id": mesa_id,
            "hora_inicio": None,
            "estado_mesa": 0
        }
        guardar_usuarios_activos()
        enviar_dato_serial(f"%,{mesa_id},0\n")

    def enviar_dato_serial(dato):
        print(f"Enviando dato serial: {dato}")
        ser.write(dato.encode())

    def consultar_id(button_id, estadoMesa):
        close_dlg()
        if estadoMesa == 0:
            FechaHora_Inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            actualizar_usuario_activo(str(button_id), FechaHora_Inicio, 1)
            if button_id in button_refs:
                button_refs[button_id].bgcolor = color_ocupado  # Cambia a rojo para mostrar ocupado
                button_refs[button_id].content = estado_ocupado(button_id)
        else:
            desactivar_usuario_activo(str(button_id))
            if button_id in button_refs:
                button_refs[button_id].bgcolor = color_disponible  # Cambia a azul para mostrar disponible
                button_refs[button_id].content = estado_disponible(button_id)
        page.update()

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
            title=ft.Text(f"Ocupar mesa {button_id}", size=30, text_align=ft.TextAlign.CENTER),
            icon = ft.Icon(name=ft.icons.TABLE_RESTAURANT, color=ft.colors.GREEN_400, size=40),
            content=ft.Text("¿Confirmar acción?", size=25, text_align=ft.TextAlign.CENTER),
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
            title=ft.Text(f"Desocupar mesa {button_id}", size=30, text_align=ft.TextAlign.CENTER),
            icon = ft.Icon(name=ft.icons.TABLE_RESTAURANT, color=ft.colors.GREEN_400, size=40),
            content=ft.Text("¿Confirmar acción?", size=25, text_align=ft.TextAlign.CENTER),
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

    def comprobar_mesa_activa(button_id):
        global usuarios_activos
        mesa = usuarios_activos.get(str(button_id))
        if mesa:
            return mesa['estado_mesa']
        return 0

    def handle_button_click(e, button_id):        
        print(f"Button {button_id} was pressed")
        estadoMesa = comprobar_mesa_activa(button_id)
        print(estadoMesa)
        if (estadoMesa == 1):
            dlg_modal = desocuparMesa(button_id, estadoMesa)
        else:
            dlg_modal = solicitudMesa(button_id, estadoMesa)
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def EspacioButton(button_id, texto, subtexto, on_click):
        bgcolor = color_disponible
        estado = estado_disponible(button_id)
        mesa = usuarios_activos.get(str(button_id))
        if mesa and mesa['estado_mesa'] == 1:
            bgcolor = color_ocupado
            estado = estado_ocupado(button_id)

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

    cargar_usuarios_activos()

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
