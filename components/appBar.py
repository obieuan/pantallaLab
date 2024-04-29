from flet import *
import flet_router as fr
from pages.baseUrl import router


class appBarObi:
    
    @staticmethod
    def go_about(router, e):
        router.go_push(
            fr.Location(
                name="about"
            )
        )
    
    @staticmethod
    def go_home(router, e):
        router.go_push(
            fr.Location(
                name="home"
            )
        )

    @staticmethod
    def go_calendar(router, e):
        router.go_push(
            fr.Location(
                name="calendar"
            )
        )

    @staticmethod
    def navigation_bar(router, page):
        return Row(controls=[
            Container(
                content=ElevatedButton("Go About", on_click=lambda e: appBarObi.go_about(router, e)),
                width=80,
                height=80,
                alignment=alignment.center,
                bgcolor=colors.WHITE,
                border_radius=10,
            ),
            Container(
                content=ElevatedButton("Go Home", on_click=lambda e: appBarObi.go_home(router, e)),
                width=80,
                height=80,
                alignment=alignment.center,
                bgcolor=colors.WHITE,
                border_radius=10,
            ),
            Container(
                content=ElevatedButton("Go Calendar", on_click=lambda e: appBarObi.go_calendar(router, e)),
                width=80,
                height=80,
                alignment=alignment.center,
                bgcolor=colors.WHITE,
                border_radius=10,
            )
        ])