"""
Cliente API Laravel - Integración con sistema externo
"""
import requests
import logging
from config.settings import API_URL, API_TOKEN

logger = logging.getLogger(__name__)


class LaravelClient:
    """Cliente para API Laravel"""
    
    def __init__(self):
        self.base_url = API_URL
        self.token = API_TOKEN
    
    def _post(self, comando: str, parametros: dict = None) -> dict:
        """
        Hace request POST a la API
        
        Args:
            comando: Nombre del comando (Iniciar, Finalizar, etc)
            parametros: Parámetros adicionales
            
        Returns:
            dict con respuesta de la API
        """
        payload = {
            "Comando": comando,
            "TokenApi": self.token
        }
        
        if parametros:
            payload.update(parametros)
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            logger.error("Timeout conectando con API Laravel")
            return {"Codigo": "ERROR", "Mensaje": "Timeout"}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en API Laravel: {e}")
            return {"Codigo": "ERROR", "Mensaje": str(e)}
    
    def iniciar_espacio(self, mesa_id: int, matricula: str) -> tuple[bool, str]:
        """
        Inicia sesión en una mesa
        
        Returns:
            (success, mensaje)
        """
        logger.info(f"API: Iniciar Mesa {mesa_id} - {matricula}")
        
        response = self._post("Iniciar", {
            "idEspacio": mesa_id,
            "Matricula": matricula
        })
        
        codigo = response.get("Codigo", "ERROR")
        mensaje = response.get("Mensaje", "Error desconocido")
        
        # Códigos de éxito y error
        if codigo == "1":
            logger.info(f"✓ API OK: {mensaje}")
            return True, mensaje
        elif codigo == "1608":
            return False, "Mesa ya está ocupada"
        elif codigo == "1609":
            return False, "Ya tienes otra mesa activa"
        elif codigo == "1604":
            return False, "Matrícula no encontrada"
        else:
            logger.warning(f"API error {codigo}: {mensaje}")
            return False, mensaje
    
    def finalizar_espacio(self, mesa_id: int, matricula: str) -> tuple[bool, str]:
        """
        Finaliza sesión en una mesa
        
        Returns:
            (success, mensaje)
        """
        logger.info(f"API: Finalizar Mesa {mesa_id} - {matricula}")
        
        response = self._post("Finalizar", {
            "idEspacio": mesa_id,
            "Matricula": matricula
        })
        
        codigo = response.get("Codigo", "ERROR")
        mensaje = response.get("Mensaje", "Error desconocido")
        
        if codigo == "1":
            logger.info(f"✓ API OK: {mensaje}")
            return True, mensaje
        elif codigo == "1620":
            return False, "Mesa no está iniciada"
        elif codigo == "1621":
            return False, "Esta mesa no te pertenece"
        else:
            logger.warning(f"API error {codigo}: {mensaje}")
            return False, mensaje
    
    def obtener_info_alumno(self, matricula: str) -> tuple[bool, dict]:
        """
        Obtiene información de un alumno
        
        Returns:
            (success, datos)
        """
        response = self._post("InfoAlumno", {
            "Matricula": matricula
        })
        
        if response.get("Codigo") == "1":
            return True, response.get("Datos", {})
        else:
            return False, {}
    
    def obtener_todas_mesas(self) -> tuple[bool, list]:
        """
        Obtiene estado de todas las mesas desde Laravel
        
        Returns:
            (success, lista_mesas)
        """
        logger.info("Consultando InfoTodasMesas...")
        
        response = self._post("InfoTodasMesas")
        
        # Laravel devuelve directamente el array de mesas
        if isinstance(response, list):
            logger.info(f"Recibidas {len(response)} mesas de Laravel")
            return True, response
        elif isinstance(response, dict) and response.get("Codigo") == "1":
            # Por si acaso Laravel lo envuelve en un objeto
            return True, response.get("Datos", [])
        else:
            logger.error(f"Respuesta inesperada de Laravel: {response}")
            return False, []


# Instancia global
laravel_client = LaravelClient()