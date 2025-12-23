"""Configuración del sistema"""
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv('API_URL', 'https://talleres.eium.com.mx/api/v1/consulta')
API_TOKEN = os.getenv('API_TOKEN')  
if not API_TOKEN:
    raise ValueError("API_TOKEN no configurado en .env")

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///data/lab_control.db')

OPERATING_HOURS = {
    'start': os.getenv('OPERATING_HOURS_START', '07:00'),
    'end': os.getenv('OPERATING_HOURS_END', '21:00')
}

OPERATING_DAYS = [int(d.strip()) for d in os.getenv('OPERATING_DAYS', '0,1,2,3,4,5').split(',')]

GPIO_RELAY_MAP = {
    1: 2, 2: 3, 3: 4, 4: 17, 5: 27, 6: 22, 7: 10, 8: 9,
    9: 21, 10: 20, 11: 16, 12: 12, 13: 1, 14: 7, 15: 8, 16: 25,
}

RELAY_ON, RELAY_OFF = False, True
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'False') == 'True'
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
QR_TIMEOUT = int(os.getenv('QR_TIMEOUT', '15'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
