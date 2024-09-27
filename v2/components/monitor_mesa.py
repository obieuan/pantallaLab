import asyncio
import aiohttp
from components.secrets import TokenApi, urlApi
from components.api import payloadsApi  # Importamos la clase payloadsApi

class MonitorMesa:
    def __init__(self, num_mesas, update_ui_func, control_mesa_func):
        self.token_api = TokenApi
        self.url_api = urlApi
        self.num_mesas = num_mesas
        self.update_ui_func = update_ui_func
        self.control_mesa_func = control_mesa_func

    async def consultar_estado_todas_mesas(self):
        async with aiohttp.ClientSession() as session:
            payload = payloadsApi.infoTodasMesas(TokenApi)
            async with session.post(urlApi, json=payload, headers=payloadsApi.headers) as response:
                if response.status == 401:
                    print("Error: Token inválido o expirado. Verifica las credenciales.")
                    return
                elif response.status != 200:
                    print(f"Error en la API: {response.status}")
                    return
                try:
                    # Obtener la respuesta JSON
                    data = await response.json()
                    print(f"Respuesta de la API para todas las mesas: {data}")

                    # Validar que la respuesta sea una lista
                    if isinstance(data, list):
                        for mesa in data:
                            mesa_id = mesa['id']  # Accedemos al id de cada mesa
                            estado = mesa['Estado']
                            self.update_ui_func(mesa_id, estado)
                    else:
                        print("Error: La respuesta no es una lista de mesas")
                except Exception as e:
                    print(f"Error al procesar la respuesta de la API: {e}")



    async def monitor_estado_mesas(self):
        while True:
            estado_mesas = await self.consultar_estado_todas_mesas()
            if estado_mesas is not None:
                for mesa in estado_mesas:
                    mesa_id = mesa['id']
                    estado = mesa['Estado']
                    self.update_ui_func(mesa_id, estado)  # Actualiza la UI
                    self.control_mesa_func(mesa_id, estado)  # Controla la energía física de las mesas
            await asyncio.sleep(10)  # Verificar cada 10 segundos
