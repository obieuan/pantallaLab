"""
Control de GPIO - Módulo de Relés
"""
import logging
from config.settings import GPIO_RELAY_MAP, RELAY_ON, RELAY_OFF

logger = logging.getLogger(__name__)

# Intentar importar RPi.GPIO
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("⚠ RPi.GPIO no disponible - Modo simulación")


class RelayController:
    """Controlador de relés GPIO"""
    
    def __init__(self):
        self.gpio_available = GPIO_AVAILABLE
        self.relay_states = {i: False for i in range(1, 17)}
        
        if self.gpio_available:
            self._setup_gpio()
        else:
            logger.info("Modo simulación - No se controlarán relés reales")
    
    def _setup_gpio(self):
        """Configura pines GPIO"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            for mesa_id, pin in GPIO_RELAY_MAP.items():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, RELAY_OFF)
            
            logger.info("✓ GPIO configurado correctamente")
        except Exception as e:
            logger.error(f"Error configurando GPIO: {e}")
            self.gpio_available = False
    
    def turn_on(self, mesa_id: int) -> bool:
        """Enciende relé de una mesa"""
        if mesa_id not in GPIO_RELAY_MAP:
            logger.error(f"Mesa {mesa_id} no existe en mapa GPIO")
            return False
        
        if self.gpio_available:
            try:
                pin = GPIO_RELAY_MAP[mesa_id]
                GPIO.output(pin, RELAY_ON)
                logger.info(f"✓ Mesa {mesa_id} (GPIO {pin}) ENCENDIDA")
            except Exception as e:
                logger.error(f"Error encendiendo Mesa {mesa_id}: {e}")
                return False
        else:
            logger.info(f"[SIMULACIÓN] Mesa {mesa_id} encendida")
        
        self.relay_states[mesa_id] = True
        return True
    
    def turn_off(self, mesa_id: int) -> bool:
        """Apaga relé de una mesa"""
        if mesa_id not in GPIO_RELAY_MAP:
            logger.error(f"Mesa {mesa_id} no existe en mapa GPIO")
            return False
        
        if self.gpio_available:
            try:
                pin = GPIO_RELAY_MAP[mesa_id]
                GPIO.output(pin, RELAY_OFF)
                logger.info(f"✓ Mesa {mesa_id} (GPIO {pin}) APAGADA")
            except Exception as e:
                logger.error(f"Error apagando Mesa {mesa_id}: {e}")
                return False
        else:
            logger.info(f"[SIMULACIÓN] Mesa {mesa_id} apagada")
        
        self.relay_states[mesa_id] = False
        return True
    
    def turn_off_all(self):
        """Apaga todos los relés"""
        logger.info("Apagando todos los relés...")
        for mesa_id in range(1, 17):
            self.turn_off(mesa_id)
        logger.info("✓ Todos los relés apagados")
    
    def get_state(self, mesa_id: int) -> bool:
        """Obtiene estado de un relé"""
        return self.relay_states.get(mesa_id, False)
    
    def cleanup(self):
        """Limpia GPIO al cerrar aplicación"""
        if self.gpio_available:
            try:
                self.turn_off_all()
                GPIO.cleanup()
                logger.info("✓ GPIO limpiado")
            except Exception as e:
                logger.error(f"Error limpiando GPIO: {e}")


# Instancia global
relay_controller = RelayController()