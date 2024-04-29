from flet import *
import flet_router as fr
from .baseUrl import router
from components.appBar import *

logo_superior_width = 400
logo_superior_height = 200
logo_inferior_width = 150
logo_inferior_height = 150

logo_superior = Image(src=f"./assets/logosup.png",width=logo_superior_width,height=logo_inferior_width,fit=ImageFit.CONTAIN,)    
logo_inferior = Image(src=f"./assets/logo_eium.png",width=logo_inferior_width,height=logo_inferior_height,fit=ImageFit.CONTAIN,)


@router.route(name="home",path="/")
async def home(router: fr.FletRouter, page:Page):
    
    print("Entrando a la página home")

    return View(
        controls=[
            Column(controls=[
                Row([
                    Container(
                        content = logo_superior,
                        alignment = alignment.center,
                        bgcolor = colors.WHITE,
                        width = 984,
                        height=150,
                        border_radius=10,
                    )
                ]),
                Row([
                    Container(
                        content=Text("Proyecto desarrollado para el laboratorio de Ingeniería. \nCopyright 2024. by ObiEuan"),
                        alignment=alignment.center,
                        bgcolor=colors.WHITE,
                        width=984,
                        height=150,
                        border_radius=10,
                        on_click=lambda e: appBarObi.go_about(router, e)
                    )
                ]),
                appBarObi.navigation_bar(router, page),
            ])
        ]
    )

