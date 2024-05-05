

class payloadsApi:
    headers = {'Content-Type': 'application/json'}

    def informacionApi(TokenApi,button_id):
        payload = {
            "TokenApi": TokenApi,
            "TarjetaAlumno": 1, #puede ser cualquier cosa
            "Comando": "Informacion",
            "idEspacio": button_id
        }
        return payload
    
    def iniciarMesaApi(TokenApi,rfid_data,button_id):
        payload = {
            "TokenApi": TokenApi,
            "TarjetaAlumno": rfid_data,
            "Comando": "Iniciar",
            "idEspacio": button_id 
        }
        return payload
    
    def informacionUsuarioApi(TokenApi,rfid_data,button_id):
        payload = {
            "TokenApi": TokenApi,
            "TarjetaAlumno": rfid_data,
            "Comando": "InfoAlumno",
            "idEspacio": button_id
        }
        return payload
    