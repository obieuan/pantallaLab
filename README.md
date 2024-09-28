
# Gestión de Mesas API

Este proyecto gestiona el uso de mesas en un taller utilizando una API. Los usuarios pueden iniciar y finalizar mesas mediante solicitudes POST que se envían a la API. El sistema maneja autenticación mediante un token, y cada mesa está asociada a un usuario específico identificado por su matrícula.

## Características Principales

- **Iniciar mesa**: Permite a los usuarios (alumnos) inicializar una mesa con su tarjeta de identificación (matrícula).
- **Finalizar mesa**: Permite que los usuarios finalicen el uso de una mesa previamente iniciada.
- **Monitoreo del estado de las mesas**: El sistema consulta continuamente el estado de las mesas para asegurar que la interfaz se mantenga actualizada.

## Requisitos

- Python 3.7+
- Librerías adicionales:
  - `requests`
  - `asyncio`
  
Puedes instalarlas usando pip:

```bash
pip install requests asyncio
```

## Configuración del Proyecto

1. Clona este repositorio en tu máquina local.
2. Crea un archivo `secrets.py` que contenga las variables `TokenApi` y `urlApi` necesarias para la autenticación y la comunicación con la API:

```python
# secrets.py
TokenApi = "YOUR_TOKEN_API"
urlApi = "https://api.ejemplo.com/mesas"
```

3. Define los payloads que se enviarán a la API en el archivo `payloadsApi.py`:

```python
# payloadsApi.py
headers = {'Content-Type': 'application/json'}

def iniciarMesaApi(token, tarjeta_alumno, id_mesa):
    return {
        "TokenApi": token,
        "Comando": "Iniciar",
        "Matricula": tarjeta_alumno,
        "idEspacio": id_mesa
    }

def finalizarMesaApi(token, tarjeta_alumno, id_mesa):
    return {
        "TokenApi": token,
        "Comando": "Finalizar",
        "Matricula": tarjeta_alumno,
        "idEspacio": id_mesa
    }
```

## Estructura del Proyecto

```bash
.
├── main.py                # Archivo principal donde se gestionan las mesas
├── payloadsApi.py         # Archivo que genera los payloads para las solicitudes API
├── monitor.py             # Archivo para consultar el estado de todas las mesas
├── secrets.py             # Token y URL de la API
└── README.md              # Documentación del proyecto
```

## Funcionamiento

### Iniciar Mesa

La función `iniciar_mesa` se encarga de enviar una solicitud POST a la API para iniciar una mesa. Se espera que el servidor responda con un código `200` y un código de éxito en el JSON:

```python
# Función para iniciar una mesa
def iniciar_mesa(tarjeta_alumno, button_id):
    # Genera el payload con los datos del alumno y la mesa
    payload = payloadsApi.iniciarMesaApi(TokenApi, tarjeta_alumno, button_id)

    # Enviar el payload a la API
    response = requests.post(urlApi, json=payload, headers=payloadsApi.headers)

    # Manejo de la respuesta
    if response.status_code == 200:
        response_json = response.json()
        if response_json['Codigo'] == '1':
            print(f"Mesa {button_id} iniciada correctamente")
            # Actualiza el estado de las mesas
            asyncio.run(monitor.consultar_estado_todas_mesas())
        else:
            manejar_error(response_json['Codigo'])
    else:
        print("Error de comunicación con la API")
```

### Finalizar Mesa

La función `finalizar_mesa` se encarga de finalizar una mesa en uso. La API responde con un código `200` y un código en el JSON que indica si la operación fue exitosa o no:

```python
# Función para finalizar una mesa
def finalizar_mesa(tarjeta_alumno, button_id):
    payload = payloadsApi.finalizarMesaApi(TokenApi, tarjeta_alumno, button_id)
    
    response = requests.post(urlApi, json=payload, headers=payloadsApi.headers)

    if response.status_code == 200:
        response_json = response.json()
        if response_json['Codigo'] == '1':
            print(f"Mesa {button_id} finalizada correctamente")
            asyncio.run(monitor.consultar_estado_todas_mesas())
        else:
            manejar_error(response_json['Codigo'])
    else:
        print("Error de comunicación con la API")
```

### Manejo de Errores

El sistema verifica el campo `"Codigo"` dentro de la respuesta JSON para identificar el tipo de error y mostrar mensajes apropiados al usuario:

```python
def manejar_error(codigo):
    if codigo == '1601':
        print("Error: Parámetros no válidos.")
    elif codigo == '1602':
        print("Error: Token no válido.")
    elif codigo == '1603':
        print("Error: Se requiere la matrícula.")
    elif codigo == '1604':
        print("Error: Matrícula no encontrada.")
    elif codigo == '1605':
        print("Error: El espacio no existe.")
    elif codigo == '1608':
        print("Error: El espacio ya ha sido iniciado anteriormente.")
    elif codigo == '1609':
        print("Error: El alumno ya tiene un espacio activo.")
    elif codigo == '1620':
        print("Error: El espacio no ha sido iniciado.")
    elif codigo == '1621':
        print("Error: El espacio no corresponde al usuario.")
    else:
        print(f"Error desconocido: {codigo}")
```

## Ejecución del Proyecto

Para iniciar el sistema de gestión de mesas, simplemente ejecuta el archivo `main.py`. Asegúrate de que los archivos `secrets.py` y `payloadsApi.py` estén correctamente configurados.

```bash
python main.py
```

## Posibles Errores

A continuación se muestran algunos de los errores más comunes que puede devolver la API:

- **1601**: Error en los parámetros enviados.
- **1602**: Token de autenticación no válido.
- **1603**: Matrícula no proporcionada.
- **1604**: Matrícula no encontrada en el sistema.
- **1605**: Espacio no encontrado.
- **1608**: El espacio ya ha sido iniciado.
- **1609**: El alumno ya tiene un espacio activo.
- **1620**: El espacio no ha sido iniciado.
- **1621**: El espacio no corresponde al usuario.

## Monitoreo de Mesas

La aplicación está diseñada para monitorear el estado de todas las mesas a través de la función `consultar_estado_todas_mesas`, que se ejecuta cada vez que se realiza una operación para mantener la información actualizada.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
