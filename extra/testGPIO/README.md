# ⚡ GPIO Tester - Prueba de Relés

Proyecto simple para testear la instalación eléctrica de las 16 mesas.

## 🎯 Propósito

- Testear que los 16 relés prendan y apaguen correctamente
- Verificar cableado GPIO
- Probar interfaz táctil en Raspberry Pi
- **No requiere internet ni base de datos**

## 📋 Requisitos

Solo necesitas Flask en la Raspberry Pi:

```bash
pip install Flask
```

## 🚀 Instalación en Raspberry Pi

```bash
# 1. Copiar carpeta al Pi
scp -r gpio-tester pi@192.168.x.x:~/

# 2. En el Pi
cd ~/gpio-tester
pip install Flask

# 3. Ejecutar
python3 app.py
```

## 🖥️ Uso

1. **Ejecutar el servidor:**
   ```bash
   python3 app.py
   ```

2. **Abrir navegador en el Pi:**
   - URL: `http://localhost:5000`
   - O desde otra PC: `http://IP-DEL-PI:5000`

3. **Testear:**
   - Click en cada mesa para encender/apagar
   - Verifica que el relé físico se active
   - Escucha el "click" del relé
   - Verifica que llegue voltaje a la mesa

4. **Botón de emergencia:**
   - "APAGAR TODO" apaga todos los relés de golpe

## 🔌 Mapeo GPIO (BCM)

```
Mesa 1  → GPIO 2    |  Mesa 9  → GPIO 21
Mesa 2  → GPIO 3    |  Mesa 10 → GPIO 20
Mesa 3  → GPIO 4    |  Mesa 11 → GPIO 16
Mesa 4  → GPIO 17   |  Mesa 12 → GPIO 12
Mesa 5  → GPIO 27   |  Mesa 13 → GPIO 1  (Soldadura 1)
Mesa 6  → GPIO 22   |  Mesa 14 → GPIO 7  (Soldadura 2)
Mesa 7  → GPIO 10   |  Mesa 15 → GPIO 8
Mesa 8  → GPIO 9    |  Mesa 16 → GPIO 25
```

## ✅ Checklist de Prueba

- [ ] Servidor inicia sin errores
- [ ] Interfaz carga en navegador
- [ ] Click en Mesa 1 → Relé 1 hace "click"
- [ ] Click en Mesa 2 → Relé 2 hace "click"
- [ ] ... probar todas las 16 mesas
- [ ] Botón "APAGAR TODO" funciona
- [ ] Todas las mesas apagan correctamente

## 🎨 Características de la Interfaz

- **Verde brillante**: Mesa encendida (con animación)
- **Gris**: Mesa apagada
- **Layout**: Igual al laboratorio real
- **Muestra GPIO**: Número de pin BCM debajo de cada mesa
- **Táctil**: Optimizado para pantalla touch

## 🐛 Troubleshooting

### "Permission denied" en GPIO
```bash
sudo usermod -a -G gpio $USER
# Logout y login de nuevo
```

### Puerto 5000 ocupado
Cambia el puerto en `app.py` línea 115:
```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

### GPIO no funciona
Verifica que estés en Raspberry Pi:
```bash
# Este comando debe mostrar la versión
cat /proc/cpuinfo | grep Model
```

## 📁 Estructura

```
gpio-tester/
├── app.py              # Backend Flask con control GPIO
├── templates/
│   └── index.html      # Interfaz táctil
└── README.md           # Este archivo
```

## ⚠️ Importante

- **Lógica invertida**: Los relés se activan con LOW (normal en módulos relé)
- **Apagar al terminar**: Siempre apaga todos los relés antes de cerrar
- **Ctrl+C**: Para salir limpiamente (ejecuta GPIO.cleanup())

## 🔧 Modificar Mapeo de Pines

Si tu cableado es diferente, edita `app.py` líneas 24-31:

```python
GPIO_RELAY_MAP = {
    1: 2,   # Cambia el número del pin aquí
    2: 3,
    # ...
}
```

## 💡 Tips

1. **Prueba una por una**: Primero prueba Mesa 1, luego 2, etc.
2. **Escucha el click**: Deberías oír el relé activarse
3. **Mide voltaje**: Usa multímetro para verificar salida
4. **Marca las que fallan**: Anota cuáles no funcionan para revisar cableado

---

**Desarrollado para testeo EIUM - 2024**
