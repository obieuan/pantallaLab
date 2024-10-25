import flet as ft
import asyncio

def main(page: ft.Page):
    # Configuraciones generales
    page.title = "Sci-Fi Numeric Panel"
    page.window.width = 1024
    page.window.height = 600
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.DARK  # Modo oscuro para un estilo más futurista

    # Variables para las medidas
    boton_ancho = 130
    boton_alto = 80
    text_size_boton = 24  # Tamaño del texto de los botones
    panel_numeros_alto = 100  # Ajustado para ser un poco menos alto
    panel_numeros_padding = 20
    espacio_abajo_botones = 50
    radio_bordes = 10
    borde_color = ft.colors.LIGHT_GREEN_ACCENT
    boton_bgcolor = ft.colors.BLUE_GREY_900
    boton_text_color = ft.colors.GREEN_ACCENT_400
    panel_bgcolor = ft.colors.BLUE_GREY_800

    # Variables para el popup
    popup_ancho = 400
    popup_alto = 200

    # Password correcto
    password_correcto = "1234"

    # Campo para mostrar el código ingresado, centrado
    campo_clave = ft.Text(
        value="", 
        size=48, 
        color=ft.colors.WHITE, 
        weight=ft.FontWeight.BOLD, 
        text_align=ft.TextAlign.CENTER
    )

    # Función para cerrar el popup después de un par de segundos y borrar el texto
    async def cerrar_popup():
        await asyncio.sleep(2)  # Espera de 2 segundos
        page.dialog.open = False
        campo_clave.value = ""  # Limpiar el campo después de que el popup se cierre
        page.update()

    # Popup para mostrar el resultado
    def mostrar_popup(mensaje, color_fondo):
        page.dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Text(mensaje, size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                padding=ft.padding.all(40),
                width=popup_ancho,
                height=popup_alto
            ),
            bgcolor=color_fondo,
            modal=True,
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        page.dialog.open = True
        page.update()
        asyncio.run(cerrar_popup())  # Cierra el popup después de 2 segundos

    # Función para agregar dígitos al campo
    def agregar_numero(e):
        campo_clave.value += e.control.data
        campo_clave.update()

    # Función para borrar el último dígito
    def retroceder(e):
        campo_clave.value = campo_clave.value[:-1]
        campo_clave.update()

    # Función para verificar el código ingresado
    def enviar_codigo(e):
        if campo_clave.value == password_correcto:
            mostrar_popup("SISTEMA DESACTIVADO", ft.colors.GREEN)
        else:
            mostrar_popup("ERROR", ft.colors.RED)

    # Estilo de los botones
    button_style = ft.ButtonStyle(
        bgcolor={"": boton_bgcolor},  # Color oscuro estilo sci-fi
        color={"": boton_text_color},  # Números verdes
        shape=ft.RoundedRectangleBorder(radius=radio_bordes),  # Bordes ligeramente redondeados
        overlay_color=ft.colors.LIGHT_BLUE_100,  # Efecto de pulsado
        side=ft.BorderSide(width=1, color=borde_color),
        elevation=5,
        text_style=ft.TextStyle(size=text_size_boton)  # Tamaño del texto controlado por variable
    )

    # Fila 1: Números 9, 8, 7
    fila1 = ft.Row(
        controls=[
            ft.ElevatedButton(text="9", data="9", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="8", data="8", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="7", data="7", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Fila 2: Números 6, 5, 4
    fila2 = ft.Row(
        controls=[
            ft.ElevatedButton(text="6", data="6", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="5", data="5", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="4", data="4", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Fila 3: Números 3, 2, 1
    fila3 = ft.Row(
        controls=[
            ft.ElevatedButton(text="3", data="3", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="2", data="2", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="1", data="1", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Fila 4: Botón de Borrar, Número 0 y Enter
    fila4 = ft.Row(
        controls=[
            ft.ElevatedButton(text="⌫", on_click=retroceder, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="0", data="0", on_click=agregar_numero, width=boton_ancho, height=boton_alto, style=button_style),
            ft.ElevatedButton(text="Enter", on_click=enviar_codigo, width=boton_ancho, height=boton_alto, style=button_style)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Agregar todo al layout
    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    content=campo_clave,
                    alignment=ft.alignment.center,
                    bgcolor=panel_bgcolor,
                    padding=ft.padding.all(panel_numeros_padding),
                    border_radius=radio_bordes,
                    height=panel_numeros_alto,
                    margin=ft.margin.only(bottom=20)
                ),
                fila1,
                fila2,
                fila3,
                fila4,
                ft.Container(height=espacio_abajo_botones),  # Espacio pequeño después de los botones
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
    )

ft.app(target=main)
