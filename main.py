import flet as ft
from flet import Column, Container, Page, Row, Text, colors, icons

def main(page: Page):
    page.adaptive = True
    page.window_always_on_top = True
    page.window_width = 1024
    page.window_height = 600
    page.window_resizable = False
    page.appbar = ft.AppBar(
        title=ft.Text("Mesas de trabajo"),
        bgcolor=colors.with_opacity(0.1, ft.cupertino_colors.SYSTEM_BACKGROUND),
    )

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
    

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def solicitudMesa():
        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Para apartar"),
            content=ft.Text("¿Confirmar acción?"),
            actions=[
                ft.TextButton("Sí", on_click=close_dlg),
                ft.TextButton("No", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    dlg_modal = solicitudMesa()

    def handle_button_click(e, button_id):
        print(f"Button {button_id} was pressed")
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def EspacioButton(texto, subtexto, on_click):
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
                on_click=on_click,
            ),
    )

    def createRowOfButtons(buttons):
        return Row(controls=[
            EspacioButton(text, status, lambda e, text=text: handle_button_click(e, text))
            for text, status in buttons
        ], alignment=ft.MainAxisAlignment.END)

    page.add(
        ft.SafeArea(
            ft.Row([
                ft.Container(
                    content=Column(
                        controls=[
                            createRowOfButtons([("Mesa 1", "Disponible"), ("Mesa 2", "Disponible"), ("Mesa 3", "Disponible")]),
                            createRowOfButtons([("Mesa 4", "Disponible"), ("Mesa 5", "Disponible"), ("Mesa 6", "Disponible"), ("Mesa 7", "Disponible")]),
                            createRowOfButtons([("Mesa 8", "Disponible"), ("Mesa 9", "Disponible"), ("Mesa 10", "Disponible"), ("Mesa 11", "Disponible"), ("Mesa 12", "Disponible")]),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    bgcolor=colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=400,
                    width=770,
                ),
                ft.Container(
                    content=Column(
                        controls=[
                            Column(
                                controls=[
                                    EspacioButton("Soldadura 1", "Disponible", lambda e, text="Soldadura 1": handle_button_click(e, text)),
                                    EspacioButton("Soldadura 2", "Disponible", lambda e, text="Soldadura 2": handle_button_click(e, text)),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=colors.SURFACE_VARIANT,
                    border_radius=20,
                    padding=20,
                    height=400,
                    width=205,
                ),
            ]),
        )
    )

ft.app(target=main)
