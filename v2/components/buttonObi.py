import flet as ft

class buttonObi:
    def __init__(self, button_id, on_click):
        self.button_id = button_id
        self.on_click = on_click
        self.estado_mesa = 0  # 0 = Disponible, 1 = Ocupado
        self.color_ocupado = '#7E0315'  # Rojo
        self.color_disponible = '#0A3C82'  # Azul
        self.bgcolor = self.color_disponible
        self.estado = self._estado_disponible()

        self.button = ft.Container(
            content=self.estado,
            alignment=ft.alignment.center,
            bgcolor=self.bgcolor,
            height=115,
            width=135,
            border_radius=10,
            ink=True,
            on_click=self._handle_click
        )

    def _estado_ocupado(self):
        return ft.Column(
            [
                ft.Text(value=f"Botón {self.button_id}", size=15, color=ft.colors.WHITE),
                ft.Text(value="Ocupado", size=10, color=ft.colors.WHITE)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def _estado_disponible(self):
        return ft.Column(
            [
                ft.Text(value=f"Botón {self.button_id}", size=15, color=ft.colors.WHITE),
                ft.Text(value="Disponible", size=10, color=ft.colors.WHITE)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def _handle_click(self, e):
        self.on_click(e, self.button_id)

    def actualizar_estado(self, nuevo_estado):
        self.estado_mesa = nuevo_estado
        self.bgcolor = self.color_disponible if nuevo_estado == 0 else self.color_ocupado
        self.estado = self._estado_disponible() if nuevo_estado == 0 else self._estado_ocupado()
        self.button.content = self.estado
        self.button.bgcolor = self.bgcolor

    def obtener_boton(self):
        return self.button
