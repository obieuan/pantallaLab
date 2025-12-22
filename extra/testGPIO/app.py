"""
GPIO Tester - Prueba simple de relés
Solo para testear instalación eléctrica
"""
from flask import Flask, render_template, jsonify, request
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar importar RPi.GPIO
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    logger.info("✓ GPIO disponible")
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("⚠ GPIO no disponible - Modo simulación")

app = Flask(__name__)

# Mapeo de mesas a pines GPIO (BCM)
GPIO_RELAY_MAP = {
    # Relés 1-8: Columna izquierda
    1: 2,   2: 3,   3: 4,   4: 17,
    5: 27,  6: 22,  7: 10,  8: 9,
    # Relés 9-16: Columna derecha (de abajo a arriba)
    9: 21,  10: 20, 11: 16, 12: 12,
    13: 1,  14: 7,  15: 8,  16: 25,
}

# Lógica invertida (LOW=ON, HIGH=OFF)
RELAY_ON = False
RELAY_OFF = True

# Estado de los relés
relay_states = {i: False for i in range(1, 17)}


def setup_gpio():
    """Inicializa GPIO"""
    if not GPIO_AVAILABLE:
        logger.info("Modo simulación - No se configurará GPIO")
        return
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for mesa_id, pin in GPIO_RELAY_MAP.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, RELAY_OFF)
            logger.info(f"GPIO {pin} (Mesa {mesa_id}) configurado")
        
        logger.info("✓ Todos los GPIO configurados y apagados")
    except Exception as e:
        logger.error(f"Error configurando GPIO: {e}")


def turn_on(mesa_id):
    """Enciende un relé"""
    if mesa_id not in GPIO_RELAY_MAP:
        return False
    
    if GPIO_AVAILABLE:
        pin = GPIO_RELAY_MAP[mesa_id]
        GPIO.output(pin, RELAY_ON)
        logger.info(f"✓ Mesa {mesa_id} (GPIO {pin}) ENCENDIDA")
    else:
        logger.info(f"[SIM] Mesa {mesa_id} ENCENDIDA")
    
    relay_states[mesa_id] = True
    return True


def turn_off(mesa_id):
    """Apaga un relé"""
    if mesa_id not in GPIO_RELAY_MAP:
        return False
    
    if GPIO_AVAILABLE:
        pin = GPIO_RELAY_MAP[mesa_id]
        GPIO.output(pin, RELAY_OFF)
        logger.info(f"✓ Mesa {mesa_id} (GPIO {pin}) APAGADA")
    else:
        logger.info(f"[SIM] Mesa {mesa_id} APAGADA")
    
    relay_states[mesa_id] = False
    return True


def turn_off_all():
    """Apaga todos los relés"""
    for mesa_id in range(1, 17):
        turn_off(mesa_id)
    logger.info("✓ Todos los relés apagados")


# ========== RUTAS ==========

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/estados', methods=['GET'])
def get_estados():
    """Obtiene estados de todos los relés"""
    return jsonify({
        'success': True,
        'estados': relay_states,
        'gpio_available': GPIO_AVAILABLE
    })


@app.route('/api/toggle/<int:mesa_id>', methods=['POST'])
def toggle_mesa(mesa_id):
    """Enciende o apaga una mesa"""
    if mesa_id not in GPIO_RELAY_MAP:
        return jsonify({'success': False, 'error': 'Mesa inválida'}), 400
    
    # Toggle
    if relay_states[mesa_id]:
        turn_off(mesa_id)
        action = 'apagada'
    else:
        turn_on(mesa_id)
        action = 'encendida'
    
    return jsonify({
        'success': True,
        'mesa_id': mesa_id,
        'estado': relay_states[mesa_id],
        'mensaje': f'Mesa {mesa_id} {action}'
    })


@app.route('/api/apagar_todo', methods=['POST'])
def apagar_todo():
    """Apaga todos los relés"""
    turn_off_all()
    return jsonify({
        'success': True,
        'mensaje': 'Todos los relés apagados'
    })


if __name__ == '__main__':
    print("=" * 50)
    print("GPIO TESTER - Prueba de Relés")
    print("=" * 50)
    
    # Configurar GPIO
    setup_gpio()
    
    # Iniciar servidor
    print("\n✓ Servidor iniciado en http://localhost:5000")
    print("Abre el navegador en la Raspberry Pi\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nCerrando...")
    finally:
        turn_off_all()
        if GPIO_AVAILABLE:
            GPIO.cleanup()
        print("✓ GPIO limpiado. Adiós!")
