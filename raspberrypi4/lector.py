import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

def lecturaDeTarjeta(timeout=10):  # Timeout en segundos
    reader = SimpleMFRC522()
    start_time = time.time()  # Tiempo inicial
    text = None
    try:
        while True:
            # Verifica si el tiempo límite se ha excedido
            if time.time() - start_time > timeout:
                print("Tiempo de espera excedido")
                break
            try:
                id, text = reader.read_no_block()  # Asumiendo que existe este método
                if id:  # Si se leyó algo
                    print(text)
                    break
            except AttributeError:
                # Si 'read_no_block' no existe, usar 'read' y manejar el bloqueo de otra forma
                id, text = reader.read()
                if id:
                    print(text)
                    break
            time.sleep(1)  # Espera un segundo antes de intentar leer de nuevo para no saturar el CPU
    finally:    
        GPIO.cleanup()
    return text
