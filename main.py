import flet as ft
from flet import Column, Container, Page, Row, Text, colors, icons
#from raspberrypi4.lector import lecturaDeTarjeta
import threading


def main(page: Page):
    page.adaptive = True
    page.window_always_on_top = True
    page.window_width = 1024
    page.window_height = 600
    page.window_resizable = False
    page.window_full_screen = False
    page.appbar = ft.AppBar(
        title=ft.Text("Mesas de trabajo"),
        bgcolor=colors.with_opacity(0.1, ft.cupertino_colors.SYSTEM_BACKGROUND),
    )

    dlg_modal = None

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.CALENDAR_MONTH_OUTLINED, label="Calendario"),
            ft.NavigationDestination(icon=ft.icons.TABLE_RESTAURANT, label="Espacios"),
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

    def consultar_id(button_id):
        # Cierra el diálogo actual
        close_dlg(None)
        
        solicitarEscanear(button_id)        
        print("Button ID:", button_id)

    def close_dlg(e):
        if dlg_modal is not None:
            dlg_modal.open = False
            page.update()

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def solicitudMesa(button_id):
        nonlocal dlg_modal
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Desbloquear mesa {button_id}",size=30,text_align=ft.TextAlign.CENTER),
            icon = ft.Icon(name=ft.icons.TABLE_RESTAURANT, color=ft.colors.GREEN_400, size=40),
            content=ft.Text("¿Confirmar acción?",size=25,text_align=ft.TextAlign.CENTER),
            actions=[
                ft.IconButton(icon=ft.icons.CHECK_CIRCLE,
                    icon_color=ft.colors.GREEN_400,
                    icon_size=50,
                    tooltip="Aceptar",
                    on_click=lambda e: consultar_id(button_id)),
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
    
    def solicitarEscanear(button_id):
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
        # Inicia el temporizador para la lectura del RFID
        threading.Timer(10, check_rfid_response, args=[button_id]).start()
    
    def check_rfid_response():
        try:
            # Intenta leer el RFID
            rfid_data = lecturaDeTarjeta()  # Descomentar en la rasp
            #rfid_data = 151515  # Descomentar en la rasp
            if rfid_data:
                page.dialog.content = ft.Text(f"Dato RFID: {rfid_data}", size=25, text_align=ft.TextAlign.CENTER)
            else:
                raise ValueError("No se recibió dato")
        except Exception as e:
            page.dialog.content = ft.Text("Tiempo de espera agotado para esta solicitud", size=25, text_align=ft.TextAlign.CENTER)
            threading.Timer(3, close_dlg).start()  # Cerrar después de 3 segundos
        finally:
            page.update()

    # Inicia el temporizador para la lectura del RFID
    threading.Timer(10, check_rfid_response).start()

    def handle_button_click(e, button_id):
        print(f"Button {button_id} was pressed")
        dlg_modal = solicitudMesa(button_id)
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def EspacioButton(button_id, texto, subtexto, on_click):
        return ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value=texto, size=15,color = ft.colors.WHITE),
                        ft.Text(value=subtexto, color = ft.colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,                    
                ),
                alignment=ft.alignment.center,
                bgcolor='#0A3C82',
                height = 115,
                width = 135,
                border_radius=10,
                ink=True,
                on_click=lambda e: on_click(e, button_id),
            ),
    )

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

ft.app(target=main)
