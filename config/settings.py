"""
Configuración del sistema - Carga desde .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Directorio base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# ========== API LARAVEL ==========
API_URL = os.getenv('API_URL', 'https://talleres.eium.com.mx/api/v1/consulta')
API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise ValueError("❌ API_TOKEN no configurado en .env")

# ========== BASE DE DATOS ==========
# Usar ruta absoluta para evitar problemas con Flask instance folder
DATABASE_URI = os.getenv(
    'DATABASE_URI', 
    f'sqlite:///{os.path.join(BASE_DIR, "data", "lab_control.db")}'
)

# ========== HORARIO DE OPERACIÓN ==========
OPERATING_HOURS = {
    'start': os.getenv('OPERATING_HOURS_START', '07:00'),
    'end': os.getenv('OPERATING_HOURS_END', '21:00')
}

OPERATING_DAYS = [
    int(d.strip()) 
    for d in os.getenv('OPERATING_DAYS', '0,1,2,3,4,5').split(',')
]

# ========== GPIO ==========
GPIO_RELAY_MAP = {
    1: 2,   2: 3,   3: 4,   4: 17,
    5: 27,  6: 22,  7: 10,  8: 9,
    9: 21,  10: 20, 11: 16, 12: 12,
    13: 1,  14: 7,  15: 8,  16: 25,
}

RELAY_ON = False   # LOW = Encendido
RELAY_OFF = True   # HIGH = Apagado

# ========== SERVIDOR ==========
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ========== CÁMARA ==========
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
QR_TIMEOUT = int(os.getenv('QR_TIMEOUT', '15'))

# ========== LOGGING ==========
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')