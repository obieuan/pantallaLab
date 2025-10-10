# 🔧 PantallaLab

Sistema de gestión y control de acceso a espacios de trabajo en talleres mediante relevadores y lectura RFID, desarrollado con Python y Flet.

## 📋 Descripción

PantallaLab es una aplicación de escritorio con interfaz gráfica que permite gestionar el uso de mesas de trabajo y espacios de soldadura en un taller. Los usuarios pueden iniciar y finalizar sesiones mediante lectura de tarjetas RFID (credenciales), mientras el sistema se comunica con una API REST para controlar relevadores y monitorear el estado en tiempo real.

### ✨ Características principales

- 🎴 **Lectura RFID**: Identificación automática mediante credenciales
- 📊 **Monitoreo en tiempo real**: Visualización del estado de 14 espacios (12 mesas + 2 soldaduras)
- 🔐 **Autenticación segura**: Sistema de tokens API
- 💾 **Persistencia de sesiones**: Registro de usuarios activos en JSON
- 🎨 **Interfaz moderna**: UI desarrollada con Flet
- ⚡ **Control de relevadores**: Integración con hardware mediante API
- 🚫 **Validaciones**: Prevención de mesas duplicadas y control de vinculación usuario-mesa
- ⏱️ **Gestión de tiempo**: Registro de hora de inicio de cada sesión

## 🖥️ Interfaz

La aplicación muestra:
- **12 mesas de trabajo** organizadas en 3 filas
- **2 espacios de soldadura** en columna lateral
- Indicadores visuales por color:
  - 🔵 **Azul** (#0A3C82): Espacio disponible
  - 🔴 **Rojo** (#7E0315): Espacio ocupado

## 🛠️ Requisitos

### Software
- **Python 3.7+**
- **Sistema operativo**: Windows, Linux o macOS
- *Opcional*: Raspberry Pi 4 con lector RFID

### Hardware (Opcional)
- Lector RFID compatible
- Módulo de relevadores para control de acceso
- Credenciales RFID programadas

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/obieuan/pantallaLab.git
cd pantallaLab
```

### 2. Instalar dependencias
```bash
pip install flet requests
```

> **Nota**: `asyncio`, `threading` y `json` vienen incluidos con Python 3.7+

### 3. Estructura de archivos necesaria

Crea la siguiente estructura:
```
pantallaLab/
├── main.py
├── components/
│   ├── __init__.py
│   ├── secrets.py          # ⚠️ Configurar
│   ├── api/
│   │   ├── __init__.py
│   │   └── payloadsApi.py  # ⚠️ Configurar
│   └── usuarios_activos.json  # Se crea automáticamente
├── assets/
│   ├── logosup.png
│   └── logo_eium.png
└── raspberrypi4/           # Opcional
    └── lector.py
```

### 4. Configurar secrets.py

Crea el archivo `components/secrets.py`:
```python
# components/secrets.py
TokenApi = "TU_TOKEN_API_AQUI"
urlApi = "https://tu-api.ejemplo.com/endpoint"
```

### 5. Configurar payloadsApi.py

Crea el archivo `components/api/payloadsApi.py`:
```python
# components/api/payloadsApi.py
headers = {'Content-Type': 'application/json'}

def informacionApi(token, id_mesa):
    """Obtiene información del estado de una mesa"""
    return {
        "TokenApi": token,
        "Comando": "Informacion",
        "idEspacio": id_mesa
    }

def informacionUsuarioApi(token, rfid, id_mesa):
    """Obtiene información de un usuario por RFID"""
    return {
        "TokenApi": token,
        "Matricula": rfid,
        "idEspacio": id_mesa
    }

def iniciarMesaApi(token, rfid, id_mesa):
    """Inicia una sesión en una mesa"""
    return {
        "TokenApi": token,
        "Comando": "Iniciar",
        "Matricula": rfid,
        "idEspacio": id_mesa
    }

def finalizarMesaApi(token, rfid, id_mesa):
    """Finaliza una sesión en una mesa"""
    return {
        "TokenApi": token,
        "Comando": "Finalizar",
        "Matricula": rfid,
        "idEspacio": id_mesa
    }
```

## 🚀 Uso

### Iniciar la aplicación
```bash
python main.py
```

La ventana se abrirá en **1024x600px** y mostrará:
- Splash screen con logos institucionales
- Barra de navegación superior
- Grid de espacios disponibles/ocupados

### Flujo de trabajo

#### 📥 Iniciar sesión en una mesa

1. Usuario hace clic en una mesa **disponible** (azul)
2. Sistema muestra diálogo de confirmación
3. Usuario confirma la acción
4. Sistema solicita acercar credencial al lector RFID
5. **Validaciones automáticas**:
   - ✅ Verifica que el usuario no tenga otra mesa activa
   - ✅ Consulta información del usuario en la API
   - ✅ Registra usuario en `usuarios_activos.json`
6. Mesa cambia a **ocupado** (rojo) si es autorizado
7. Relevador se activa mediante API

#### 📤 Finalizar sesión

1. Usuario hace clic en una mesa **ocupada** (roja)
2. Sistema solicita acercar credencial
3. **Validaciones automáticas**:
   - ✅ Verifica que la mesa pertenezca al usuario
   - ✅ Elimina registro de `usuarios_activos.json`
4. Mesa cambia a **disponible** (azul)
5. Relevador se desactiva

## 📁 Estructura del Proyecto

```
pantallaLab/
├── main.py                      # Aplicación principal con lógica de UI
├── components/
│   ├── secrets.py              # Token y URL de API (git-ignored)
│   ├── usuarios_activos.json   # Registro de sesiones activas
│   └── api/
│       └── payloadsApi.py      # Generador de payloads para API
├── assets/
│   ├── logosup.png            # Logo institucional superior
│   └── logo_eium.png          # Logo EIUM
├── raspberrypi4/              # Módulo de hardware (opcional)
│   └── lector.py              # Funciones de lectura RFID
└── README.md
```

## 🔌 Documentación de API

### 📍 Endpoint Base
```
POST {urlApi}
```

### 🔑 Autenticación
Todas las peticiones requieren `TokenApi` en el payload.

---

### 1️⃣ Obtener información de mesa

**Payload**:
```json
{
  "TokenApi": "string",
  "Comando": "Informacion",
  "idEspacio": "string"
}
```

**Respuesta exitosa**:
```json
{
  "id": "1",
  "Estado": 0,
  "user_id": null,
  "FechaHora_Inicio": null
}
```

---

### 2️⃣ Consultar información de usuario

**Payload**:
```json
{
  "TokenApi": "string",
  "Matricula": "string",
  "idEspacio": "string"
}
```

**Respuesta exitosa**:
```json
{
  "id": "12345",
  "nombre": "Juan Pérez",
  "Codigo": "1"
}
```

---

### 3️⃣ Iniciar mesa

**Payload**:
```json
{
  "TokenApi": "string",
  "Comando": "Iniciar",
  "Matricula": "string",
  "idEspacio": "string"
}
```

**Respuesta exitosa**:
```json
{
  "Codigo": "1",
  "Mensaje": "Mesa iniciada correctamente"
}
```

---

### 4️⃣ Finalizar mesa

**Payload**:
```json
{
  "TokenApi": "string",
  "Comando": "Finalizar",
  "Matricula": "string",
  "idEspacio": "string"
}
```

**Respuesta exitosa**:
```json
{
  "Codigo": "1",
  "Mensaje": "Mesa finalizada correctamente"
}
```

## ⚠️ Códigos de Error

| Código | Descripción | Acción recomendada |
|--------|-------------|-------------------|
| `0` | Acceso denegado | Verificar credenciales |
| `1601` | Parámetros no válidos | Revisar estructura del payload |
| `1602` | Token no válido | Regenerar token API |
| `1603` | Matrícula no proporcionada | Verificar lectura RFID |
| `1604` | Matrícula no encontrada | Usuario no registrado en sistema |
| `1605` | Espacio no existe | Verificar ID de mesa |
| `1608` | Espacio ya iniciado | Mesa ocupada por otro usuario |
| `1609` | Usuario tiene espacio activo | Finalizar mesa anterior primero |
| `1620` | Espacio no iniciado | No se puede finalizar mesa disponible |
| `1621` | Espacio no corresponde al usuario | Solo el propietario puede finalizar |

## 🔧 Funciones Principales

### Gestión de Estado

#### `cargar_usuarios_activos()`
Carga el archivo JSON con usuarios activos al iniciar.

#### `guardar_usuario_activo(mesa_id, user_id, FechaHora_Inicio, Estado)`
Registra una nueva sesión activa en el sistema.
- **Parámetros**: ID de mesa, matrícula, timestamp, estado
- **Almacenamiento**: `usuarios_activos.json`

#### `eliminar_usuario_activo(user_id)`
Elimina el registro de sesión al finalizar.

---

### Validaciones

#### `comprobar_usuario_activo(user_id)`
Valida que el usuario no tenga una mesa activa.
- **Lanza**: `ValueError` si ya tiene mesa asignada

#### `comprobar_mesa_activa(button_id)`
Verifica el estado actual de una mesa.
- **Retorna**: Estado de la mesa o `None`

#### `comprobar_vinculacion_mesa(button_id, response_data, rfid_data, user_id)`
Valida que el usuario sea propietario de la mesa que intenta finalizar.

---

### API Requests

#### `check_rfid_response(button_id, estadoMesa)`
Gestiona el flujo completo de lectura RFID y comunicación con API.
- Lee tarjeta RFID
- Consulta información del usuario
- Ejecuta validaciones
- Inicia/finaliza mesa según corresponda
- Actualiza interfaz

---

### UI Components

#### `EspacioButton(button_id, texto, subtexto, on_click)`
Crea un botón de mesa con estado visual.
- Consulta estado actual en API
- Aplica color según disponibilidad
- Registra en `button_refs` para actualizaciones

#### `estado_ocupado(button_id)` / `estado_disponible(button_id)`
Genera el contenido visual del botón según su estado.

---

### Diálogos Modales

#### `solicitudMesa(button_id, estadoMesa)`
Diálogo de confirmación para iniciar mesa.

#### `desocuparMesa(button_id, estadoMesa)`
Diálogo de confirmación para finalizar mesa.

#### `solicitarEscanear(button_id, estadoMesa)`
Diálogo de espera durante lectura RFID.

## 🎨 Clase `buttonObi`

Componente reutilizable para botones de espacios (alternativa modular).

```python
from buttonObi import buttonObi

# Crear botón
boton = buttonObi(button_id=1, on_click=handle_click)

# Actualizar estado
boton.actualizar_estado(nuevo_estado=1)  # 0=disponible, 1=ocupado

# Obtener componente Flet
container = boton.obtener_boton()
```

## 🔒 Seguridad

- ⚠️ **NUNCA** subas `secrets.py` a Git
- Añade a `.gitignore`:
```gitignore
components/secrets.py
components/usuarios_activos.json
__pycache__/
*.pyc
```

## 🧪 Testing

Para probar sin hardware RFID, modifica en `main.py`:
```python
def check_rfid_response(button_id, estadoMesa):
    # rfid_data = lecturaDeTarjeta()  # Comentar lectura real
    rfid_data = 15136485  # Valor de prueba
```

## 🚀 Despliegue en Raspberry Pi

1. Instalar dependencias en Raspberry Pi:
```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install flet requests
```

2. Descomentar módulo de lectura RFID:
```python
from raspberrypi4.lector import lecturaDeTarjeta
```

3. Configurar inicio automático (opcional):
```bash
crontab -e
# Añadir:
@reboot python3 /ruta/pantallaLab/main.py
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/MejoraPantalla`)
3. Commit cambios (`git commit -m 'Añade animación de carga'`)
4. Push a la rama (`git push origin feature/MejoraPantalla`)
5. Abre un Pull Request

### Áreas de mejora
- [ ] Agregar base de datos en lugar de JSON
- [ ] Implementar sistema de reservas
- [ ] Panel de administración web
- [ ] Notificaciones push
- [ ] Estadísticas de uso
- [ ] Modo oscuro/claro

## 🐛 Problemas Conocidos

- El archivo `usuarios_activos.json` se reinicia al iniciar la app
- La lectura RFID está hardcodeada en modo de prueba
- No hay manejo de desconexión de red

## 📝 Changelog

### v1.0.0 (Actual)
- ✅ Interfaz gráfica con Flet
- ✅ Sistema de gestión de 14 espacios
- ✅ Integración con API REST
- ✅ Validaciones de usuario y mesa
- ✅ Registro de sesiones activas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 👥 Créditos

**Desarrollado por**: [@obieuan](https://github.com/obieuan)

**Institución**: Escuela de Ingeniería - Universidad Modelo

## 📞 Soporte

¿Tienes problemas o sugerencias?
- 🐛 Abre un [issue](https://github.com/obieuan/pantallaLab/issues)
- 💬 Inicia una [discusión](https://github.com/obieuan/pantallaLab/discussions)
- 📧 Contacta al desarrollador

---

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub**