import RPi.GPIO as GPIOfrom mfrc522 import SimpleMFRC522

def lecturaDeTarjeta():

    reader = SimpleMFRC522()
    text = ""
    try:
        id,text=reader.read()
        print(text)
    finally:    
        GPIO.cleanup()
return text