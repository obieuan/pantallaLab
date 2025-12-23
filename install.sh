#!/bin/bash

echo "======================================"
echo "  Lab Control MVP - Instalación"
echo "======================================"
echo ""

# Verificar que estamos en Raspberry Pi
if [ ! -f /proc/cpuinfo ] || ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Advertencia: No se detectó Raspberry Pi"
    echo "El sistema funcionará en modo simulación"
    echo ""
fi

# Crear entorno virtual
echo "1. Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias básicas
echo "2. Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Si estamos en Raspberry Pi, instalar hardware
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "3. Instalando librerías de hardware..."
    pip install RPi.GPIO opencv-python pyzbar
else
    echo "3. Saltando librerías de hardware (no es Raspberry Pi)"
fi

# Crear directorio de datos
mkdir -p data
mkdir -p logs

# Dar permisos
chmod +x app.py

echo ""
echo "======================================"
echo "  ✓ Instalación completada"
echo "======================================"
echo ""
echo "Para iniciar el servidor:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Luego abre: http://localhost:5000"
echo ""
