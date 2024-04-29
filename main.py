from flet import *
import flet_router as fr
from pages.baseUrl import router


#PAGES
from pages.home import home
from pages.about import about

def main(page:Page):

    page.title = "Laboratorio de Electrónica"
    page.window_width = 1024
    page.window_height = 600
    
    app_router = fr.FletRouter.mount(
        page,
        routes=router.routes
    )


    app_router.go_root("/")

app(main)