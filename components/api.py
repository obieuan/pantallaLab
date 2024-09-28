

class payloadsApi:
    headers = {'Content-Type': 'application/json'}

    def informacionApi(TokenApi,button_id):
        payload = {
            "TokenApi": TokenApi,
            "Comando": "Informacion",
            "idEspacio": button_id
        }
        return payload

    def infoTodasMesas(TokenApi):
        payload = {
            "TokenApi": TokenApi,
            "Comando": "InfoTodasMesas"
        }
        return payload
    
    def iniciarMesaApi(TokenApi,MatriculaData,button_id):
        payload = {
            "TokenApi": TokenApi,
            "Matricula": MatriculaData,
            "Comando": "Iniciar",
            "idEspacio": button_id 
        }
        return payload
    
    def informacionUsuarioApi(TokenApi,MatriculaData,button_id):
        payload = {
            "TokenApi": TokenApi,
            "Matricula": MatriculaData,
            "Comando": "InfoAlumno",
            "idEspacio": button_id
        }
        return payload
    
    def finalizarMesaApi(TokenApi,MatriculaData,button_id):
        payload = {
            "TokenApi": TokenApi,
            "Matricula": MatriculaData,
            "Comando": "Finalizar",
            "idEspacio": button_id
        }
        return payload
                        