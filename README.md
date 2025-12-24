# 🔧 Lab Control MVP - Sistema de Mesas de Laboratorio

Sistema simplificado para control de 16 mesas mediante pantalla táctil, escáner QR y relés GPIO con **sincronización bidireccional con Laravel**.

## 🎯 MVP - Funcional Mínimo

**Hardware:**
- Raspberry Pi 4
- Pantalla táctil HDMI (1024x600)
- Cámara USB (escaneo QR en tiempo real)
- Módulo 16 relés

**Funcionalidades:**
1. ✅ Visualizar 16 mesas (azul=disponible, rojo=ocupado)
2. ✅ Ocupar mesa (QR automático o teclado manual)
3. ✅ Liberar mesa  
4. ✅ Validar con API Laravel
5. ✅ Control GPIO de relés
6. ✅ Historial en SQLite
7. ✅ **Sincronización automática cada 5s** (Laravel → Raspberry Pi)
8. ✅ **Preview de cámara en vivo** durante escaneo QR
9. ✅ **Sincronización inicial** al arrancar sistema

## 📋 Requisitos

```bash
# Python 3.9+
sudo apt update
sudo apt install python3-pip python3-venv

# Librerías de sistema (Raspberry Pi)
sudo apt install python3-rpi.gpio
sudo apt install libzbar0  # Para QR
sudo apt install python3-opencv  # Para cámara
```

## 🚀 Instalación en Raspberry Pi

### 1. Copiar proyecto

```bash
# Desde tu PC (ajusta la ruta si es diferente)
scp -r pantallalab/ pi@192.168.x.x:~/pantalla/

# En el Pi
cd ~/pantalla/pantallalab
```

### 2. Instalar dependencias

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar paquetes Python
pip install -r requirements.txt
```

### 3. Configurar

```bash
# Copiar template de configuración
cp .env.example .env

# IMPORTANTE: Editar .env
nano .env
```

**Configuración mínima requerida:**
```bash
# API Laravel
API_URL=https://talleres.eium.com.mx/api/v1/consulta
API_TOKEN=tu_token_aqui

# Base de datos (RUTA ABSOLUTA)
DATABASE_URI=sqlite:////home/obieuan/pantalla/pantallalab/data/lab_control.db

# Horario (Lun-Sáb 7:00-21:00)
OPERATING_HOURS_START=07:00
OPERATING_HOURS_END=21:00
OPERATING_DAYS=0,1,2,3,4,5

# Servidor
HOST=0.0.0.0
PORT=5000

# Cámara
CAMERA_INDEX=0
QR_TIMEOUT=15
```

**⚠️ CRÍTICO:** 
- La ruta de `DATABASE_URI` debe ser **absoluta** (con 4 slashes: `sqlite:////`)
- Cambiar `/home/obieuan/` por tu usuario real
- **NUNCA subas .env a Git**

### 4. Crear directorio de datos

```bash
mkdir -p data
```

### 5. Ejecutar

```bash
python app.py
```

Deberías ver:
```
============================================================
Sincronización inicial con Laravel...
============================================================
Mesa 1: disponible
✓ Mesa 1 (GPIO 9) APAGADA
Mesa 2: ocupado (user 123)
✓ Mesa 2 (GPIO 10) ENCENDIDA
...
✓ Sincronización inicial completada
============================================================

✓ Servidor iniciado en http://0.0.0.0:5000
```

### 6. Abrir en navegador

```bash
# En el mismo Pi (modo kiosk)
chromium-browser --kiosk http://localhost:5000

# Desde otra PC en la red
http://192.168.x.x:5000
```

## 🔌 Mapeo GPIO (Actualizado)

```
Mesa  → Pin BCM  → Pin Físico
────────────────────────────────
1  → GPIO 9   → Pin 21
2  → GPIO 10  → Pin 19
3  → GPIO 22  → Pin 15
4  → GPIO 27  → Pin 13
5  → GPIO 17  → Pin 11
6  → GPIO 4   → Pin 7
7  → GPIO 3   → Pin 5
8  → GPIO 2   → Pin 3
9  → GPIO 25  → Pin 22
10 → GPIO 8   → Pin 24
11 → GPIO 7   → Pin 26
12 → GPIO 1   → Pin 28
13 → GPIO 12  → Pin 32 (Soldadura)
14 → GPIO 16  → Pin 36 (Soldadura)
15 → GPIO 20  → Pin 38 (Soldadura)
16 → GPIO 21  → Pin 40 (Soldadura)
```

**Lógica:** `LOW = Encendido`, `HIGH = Apagado` (relés activos en bajo)

## 📡 API Endpoints

### GET /api/estados
Obtiene estado de todas las mesas (desde DB local)

**Response:**
```json
{
  "success": true,
  "estados": {
    "1": {
      "id": 1,
      "estado": "disponible",
      "usuario": null,
      "hora_inicio": null
    }
  },
  "gpio_available": true,
  "qr_available": true
}
```

### POST /api/sincronizar
**NUEVO:** Sincroniza estados desde nube y actualiza GPIO

**Response:**
```json
{
  "success": true,
  "mensaje": "3 mesas sincronizadas"
}
```

Este endpoint se llama automáticamente cada 5 segundos desde el frontend.

### POST /api/ocupar
Ocupa una mesa

**Body:**
```json
{
  "mesa_id": 1,
  "matricula": "12345678"
}
```

**Flujo:**
1. Valida horario de operación
2. Valida que usuario no tenga otra mesa
3. Valida con API Laravel
4. Actualiza DB local
5. Enciende GPIO
6. Crea sesión

### POST /api/liberar
Libera una mesa

**Body:**
```json
{
  "mesa_id": 1,
  "matricula": "5454"
}
```

**Flujo:**
1. Valida que mesa esté ocupada
2. Obtiene `user_id` de la matrícula desde Laravel
3. Valida que mesa pertenezca al usuario (compara matrícula O user_id)
4. Valida con API Laravel
5. Finaliza sesión en DB local
6. Apaga GPIO

### GET /api/camera_feed
**NUEVO:** Stream MJPEG de cámara en vivo

### GET /api/qr_status
**NUEVO:** Estado del último QR detectado

**Response:**
```json
{
  "success": true,
  "qr": "12345678",
  "ts": 1703371234.567,
  "camera_running": true
}
```

### POST /api/escanear_qr
**NUEVO:** Consume el último QR detectado (limpia el buffer)

**Response:**
```json
{
  "success": true,
  "matricula": "12345678"
}
```

## 🗂️ Estructura del Proyecto

```
pantallalab/
├── app.py                      # Flask principal + sincronización
├── .env                        # Configuración (NO subir a Git)
├── .env.example                # Template de configuración
├── requirements.txt
├── config/
│   └── settings.py            # Carga .env, valida API_TOKEN
├── models/
│   └── database.py            # SQLite: Mesa, Sesion
├── hardware/
│   ├── gpio_control.py        # Control relés con mapeo invertido
│   ├── qr_scanner.py          # Escáner QR (legacy)
│   └── camera_service.py      # **NUEVO** Servicio de cámara en thread
├── api/
│   └── laravel_client.py      # Cliente API (TokenApi corregido)
├── templates/
│   └── index.html             # Interfaz táctil optimizada 1024x600
├── static/
│   └── js/
│       └── app.js             # JavaScript con preview de cámara
└── data/
    └── lab_control.db         # SQLite (auto-creado)
```

## 🔄 Flujo de Operación

### Ocupar Mesa (desde Pantalla):

```
1. Usuario toca mesa azul (disponible)
2. Modal: "Acerca tu credencial - Mesa X"
3. **Preview de cámara se activa automáticamente**
4. Sistema detecta QR cada 200ms
5. Al detectar QR numérico:
   → Cierra modal
   → Detiene cámara
   → Valida con Laravel
   → Actualiza DB local
   → Enciende GPIO
   → Mesa se pone roja
6. O: Click "Ingresar Manualmente" → Teclado en pantalla
```

### Liberar Mesa (desde Pantalla):

```
1. Usuario toca mesa roja (ocupada)
2. Confirma con su matrícula (QR o manual)
3. Validaciones:
   ✓ Mesa ocupada
   ✓ Obtiene user_id de matrícula desde Laravel
   ✓ Compara: usuario_actual == matricula O user_id
   ✓ API Laravel confirma
4. Si OK:
   → Finaliza sesión en DB
   → Apaga GPIO
   → Mesa se pone azul
```

### Sincronización Server → Pantalla (Automática):

```
Cada 5 segundos:
1. Frontend llama POST /api/sincronizar
2. Backend consulta Server (InfoTodasMesas)
3. Por cada mesa:
   Si Laravel dice ocupada Y local disponible:
     → Actualiza DB: estado=1, usuario=user_id
     → Enciende GPIO
   Si Laravel dice disponible Y local ocupada:
     → Libera mesa en DB
     → Apaga GPIO
4. Frontend actualiza UI con nuevos estados
```

### Sincronización Inicial (Al Arrancar):

```
Al ejecutar python app.py:
1. Consulta todas las mesas desde Laravel
2. Fuerza actualización de TODAS las mesas
3. Enciende/Apaga GPIO según estado Laravel
4. Garantiza que pantalla y relés coincidan con Laravel
```

## 🔮 Mejoras Futuras

- [ ] WebSocket bidireccional (reemplazar polling de 5s)
- [ ] Dashboard administrativo web
- [ ] Estadísticas: uso por hora/día, alumnos frecuentes
- [ ] Alertas: tiempo máximo, recordatorios
- [ ] Reservas anticipadas
- [ ] Multi-tenant (múltiples laboratorios)
- [ ] App móvil complementaria
- [ ] Sistema de reportes

---

**Desarrollado para EIUM**  
**Versión MVP 2.0 - Diciembre 2025**  
**Con sincronización bidireccional y preview de cámara**
