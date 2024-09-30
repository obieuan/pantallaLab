import asyncio
import aiohttp
import serial
import time
from components.secrets import TokenApi, urlApi
from components.api import payloadsApi  # Importamos la clase payloadsApi

class Mesa:
    def __init__(self, mesa_id, estado):
        self.mesa_id = mesa_id
        self.estado = estado        

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

class MonitorMesa:
    def __init__(self, num_mesas, update_ui_func, control_mesa_func):
        self.token_api = TokenApi
        self.url_api = urlApi
        self.mesas = []  # Lista para almacenar objetos de tipo Mesa
        self.update_ui_func = update_ui_func
        self.control_mesa_func = control_mesa_func
        self.accion_en_progreso = {}

    async def enviar_peticion_api(self, payload, func_confirmacion, id_mesa):
        """Envía una petición a la API y maneja la respuesta."""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url_api, json=payload, headers=payloadsApi.headers) as response:
                status = response.status
                text = await response.text()
                if status == 200:
                    data = await response.json()
                    func_confirmacion(id_mesa, data)
                else:
                    print(f"Error en la API: {status} - {text}")

    def confirmar_inicio_mesa(self, id_mesa, response_json):
        codigo = response_json.get('Codigo', '')
        if codigo == '1':
            self.update_ui_func(id_mesa, "iniciada")
            print(f"Mesa {id_mesa} iniciada correctamente.")
        else:
            self.mostrar_error(codigo)

    def confirmar_finalizacion_mesa(self, id_mesa, response_json):
        codigo = response_json.get('Codigo', '')
        if codigo == '1':
            self.update_ui_func(id_mesa, "finalizada")
            print(f"Mesa {id_mesa} finalizada correctamente.")
        else:
            self.mostrar_error(codigo)

    def mostrar_error(self, codigo):
        errores = {
            '1601': "Parámetros no válidos.",
            '1602': "Token no válido.",
            '1603': "Se requiere la matrícula para este comando.",
            '1604': "La matrícula no se encuentra en el sistema.",
            '1605': "El espacio no existe.",
            '1608': "El espacio ya ha sido iniciado anteriormente.",
            '1609': "El alumno ya tiene un espacio activo."
        }
        error_msg = errores.get(codigo, "Error desconocido.")
        print(f"Error: {error_msg}")

    async def iniciar_mesa(self, tarjeta_alumno, id_mesa):
        """Inicia una mesa específica."""
        if self.accion_en_progreso.get(id_mesa):
            print("Acción ya en progreso.")
            return
        self.accion_en_progreso[id_mesa] = True
        payload = payloadsApi.iniciarMesaApi(self.token_api, tarjeta_alumno, id_mesa)
        await self.enviar_peticion_api(payload, self.confirmar_inicio_mesa, id_mesa)
        self.accion_en_progreso[id_mesa] = False

    async def finalizar_mesa(self, tarjeta_alumno, id_mesa):
        """Finaliza una mesa específica."""
        if self.accion_en_progreso.get(id_mesa):
            print("Acción ya en progreso.")
            return
        self.accion_en_progreso[id_mesa] = True
        payload = payloadsApi.finalizarMesaApi(self.token_api, tarjeta_alumno, id_mesa)
        await self.enviar_peticion_api(payload, self.confirmar_finalizacion_mesa, id_mesa)
        self.accion_en_progreso[id_mesa] = False

    def inicializar_mesas(self, data):
        """Inicializa la lista de mesas basado en los datos obtenidos de la API."""
        self.mesas = [Mesa(mesa['id'], mesa['Estado']) for mesa in data if mesa['talleres_id'] == 1]

    def actualizar_mesas(self, data):
        """Actualiza el estado de las mesas basado en la respuesta de la API."""
        for mesa in data:
            mesa_id = mesa['id']
            estado = mesa['Estado']
            idtaller = mesa['talleres_id']
            # Filtrar solo mesas con talleres_id == 1
            if idtaller != 1:
                continue            
            mesa_obj = next((m for m in self.mesas if m.mesa_id == mesa_id), None)
            if mesa_obj:
                mesa_obj.actualizar_estado(estado)
            else:
                # Si la mesa no existe en la lista, la agregamos
                self.mesas.append(Mesa(mesa_id, estado))

    async def consultar_estado_todas_mesas(self):
        async with aiohttp.ClientSession() as session:
            payload = payloadsApi.infoTodasMesas(self.token_api)
            async with session.post(self.url_api, json=payload, headers=payloadsApi.headers) as response:
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

                    # Actualizar el estado de las mesas
                    if not self.mesas:
                        self.inicializar_mesas(data)  # Si es la primera consulta, inicializamos las mesas
                    else:
                        self.actualizar_mesas(data)  # Para futuras consultas, solo actualizamos

                    # Actualizar la UI y controlar mesas
                    for mesa_obj in self.mesas:
                        self.update_ui_func(mesa_obj.mesa_id, mesa_obj.estado)
                    estado_mesas = ";".join(f"{mesa.mesa_id},{mesa.estado}" for mesa in self.mesas) + "%"    
                    self.control_mesa_func("&"+estado_mesas)

                except Exception as e:
                    print(f"Error al procesar la respuesta de la API: {e}")
    


    async def monitor_estado_mesas(self):
        while True:
            await self.consultar_estado_todas_mesas()            
            await asyncio.sleep(30)  # Verificar cada 30 segundos

    def obtener_estado_mesa(self, mesa_id):
        """Devuelve el estado de una mesa específica si está en la lista."""
        mesa_obj = next((m for m in self.mesas if m.mesa_id == mesa_id), None)
        if mesa_obj:
            return mesa_obj.estado
        else:
            print(f"Error: Mesa {mesa_id} no encontrada.")
            return None
