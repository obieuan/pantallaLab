# 🔧 Lab Control MVP - Sistema de Mesas de Laboratorio

Sistema simplificado para control de 16 mesas mediante pantalla táctil, escáner QR y relés GPIO.

## 🎯 MVP - Funcional Mínimo

**Hardware:**
- Raspberry Pi 4
- Pantalla táctil HDMI (1024x600)
- Cámara USB
- Módulo 16 relés

**Funcionalidades:**
1. ✅ Visualizar 16 mesas (azul=disponible, rojo=ocupado)
2. ✅ Ocupar mesa (QR o teclado manual)
3. ✅ Liberar mesa  
4. ✅ Validar con API Laravel
5. ✅ Control GPIO de relés
6. ✅ Historial en SQLite

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
# Desde tu PC
scp lab-control-mvp.tar.gz pi@192.168.x.x:~/

# En el Pi
cd ~
tar -xzf lab-control-mvp.tar.gz
cd lab-control-mvp
```

### 2. Instalar dependencias

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar paquetes Python
pip install -r requirements.txt

# Instalar hardware (solo en Pi)
pip install RPi.GPIO opencv-python pyzbar
```

### 3. Configurar

```bash
# Copiar template de configuración
cp .env.example .env

# IMPORTANTE: Editar .env y poner tu token real
nano .env
# Cambiar: API_TOKEN=TU_TOKEN_AQUI

# ⚠️ NUNCA subas .env a Git
```

### 4. Probar

```bash
# Ejecutar
python app.py

# Abrir en navegador del Pi
http://localhost:5000
```

## ⚙️ Configuración (.env)

```bash
# API Laravel
API_URL=https://talleres.eium.com.mx/api/v1/consulta
API_TOKEN=tu_token_aqui

# Horario (Lun-Sáb 7:00-21:00)
OPERATING_HOURS_START=07:00
OPERATING_HOURS_END=21:00
OPERATING_DAYS=0,1,2,3,4,5

# Servidor
PORT=5000

# Cámara
CAMERA_INDEX=0
QR_TIMEOUT=15
```

## 🔌 Mapeo GPIO

```
Mesa  → Pin BCM
─────────────────
1  → GPIO 2
2  → GPIO 3
3  → GPIO 4
4  → GPIO 17
5  → GPIO 27
6  → GPIO 22
7  → GPIO 10
8  → GPIO 9
9  → GPIO 21
10 → GPIO 20
11 → GPIO 16
12 → GPIO 12
13 → GPIO 1  (Soldadura)
14 → GPIO 7  (Soldadura)
15 → GPIO 8  (Soldadura)
16 → GPIO 25 (Soldadura)
```

## 📡 API Endpoints

### GET /api/estados
Obtiene estado de todas las mesas

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
  }
}
```

### POST /api/ocupar
Ocupa una mesa

**Body:**
```json
{
  "mesa_id": 1,
  "matricula": "12345678"
}
```

**Response:**
```json
{
  "success": true,
  "mensaje": "Mesa 1 ocupada exitosamente",
  "mesa": {
    "id": 1,
    "estado": "ocupado",
    "usuario": "12345678"
  }
}
```

### POST /api/liberar
Libera una mesa

**Body:**
```json
{
  "mesa_id": 1,
  "matricula": "12345678"
}
```

### POST /api/escanear_qr
Escanea QR y retorna matrícula (requiere cámara)

**Response:**
```json
{
  "success": true,
  "matricula": "12345678"
}
```

## 🗂️ Estructura del Proyecto

```
lab-control-mvp/
├── app.py                   # Aplicación Flask principal
├── .env                      # Configuración
├── requirements.txt
├── config/
│   └── settings.py          # Settings desde .env
├── models/
│   └── database.py          # SQLite: Mesa, Sesion
├── hardware/
│   ├── gpio_control.py      # Control relés
│   └── qr_scanner.py        # Escáner QR
├── api/
│   └── laravel_client.py    # Cliente API Laravel
├── templates/
│   └── index.html           # Interfaz táctil
├── static/
│   ├── css/
│   └── js/
└── data/
    └── lab_control.db       # Base de datos (auto-creado)
```

## 🔄 Flujo de Operación

### Ocupar Mesa:

```
1. Usuario toca mesa azul (disponible)
2. Modal: "Acerca tu credencial"
3. Escanea QR o ingresa manual
4. Validaciones:
   ✓ Horario de operación
   ✓ Usuario sin otra mesa activa
   ✓ API Laravel valida matrícula
5. Si OK:
   → Actualiza DB local
   → Enciende relé GPIO
   → Mesa se pone roja
```

### Liberar Mesa:

```
1. Usuario toca mesa roja (ocupada)
2. Confirma con su matrícula
3. Validaciones:
   ✓ Mesa pertenece al usuario
   ✓ API Laravel confirma
4. Si OK:
   → Finaliza sesión en DB
   → Apaga relé GPIO
   → Mesa se pone azul
```

## 🐛 Troubleshooting

### GPIO no funciona
```bash
# Agregar usuario al grupo gpio
sudo usermod -a -G gpio $USER

# Logout y login de nuevo
```

### Cámara no detecta
```bash
# Verificar cámara
ls /dev/video*

# Probar con otro índice en .env
CAMERA_INDEX=1
```

### Puerto ocupado
```bash
# Cambiar puerto en .env
PORT=5001
```

### Base de datos bloqueada
```bash
# Detener servidor
# Borrar lock
rm data/lab_control.db-shm data/lab_control.db-wal
```

## 🔐 Permisos

```bash
# Dar permisos de ejecución
chmod +x app.py

# Si usa systemd
sudo chmod 644 /etc/systemd/system/lab-control.service
```

## 📝 Logs

```bash
# Ver logs en tiempo real
tail -f logs/lab_control.log

# Logs en consola
python app.py
```

## 🚦 Autostart (Opcional)

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/lab-control.service
```

```ini
[Unit]
Description=Lab Control MVP
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/lab-control-mvp
Environment="PATH=/home/pi/lab-control-mvp/venv/bin"
ExecStart=/home/pi/lab-control-mvp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activar
sudo systemctl enable lab-control
sudo systemctl start lab-control
sudo systemctl status lab-control
```

## 📊 Base de Datos

**Tabla: mesas**
- id (1-16)
- estado (0=disponible, 1=ocupado, 2=mantenimiento)
- usuario_actual
- hora_inicio

**Tabla: sesiones**
- id
- mesa_id
- matricula
- hora_inicio
- hora_fin
- duracion_minutos

## 🔮 Roadmap (Futuras Versiones)

- [ ] API de configuraciones desde Laravel
- [ ] Dashboard administrativo
- [ ] Estadísticas avanzadas
- [ ] Reservas
- [ ] Alertas de tiempo
- [ ] Integración SIGE
- [ ] App móvil

## 💡 Tips

1. **Testing sin hardware:** El sistema detecta automáticamente si está en Pi y activa modo simulación
2. **Cambiar horarios:** Edita `.env` y reinicia servidor
3. **Reset completo:** Borra `data/lab_control.db` y reinicia
4. **Ver BD:** `sqlite3 data/lab_control.db` luego `.tables` y `SELECT * FROM mesas;`

## 📞 Soporte

Para problemas o mejoras, contactar al equipo de desarrollo.

---

**Desarrollado para EIUM - Diciembre 2024**
**Versión MVP 1.0**
