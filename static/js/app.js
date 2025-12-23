// Lab Control MVP - Frontend JavaScript
// Conecta con Flask backend

let currentMesa = null;
let currentAction = null;
let mesasData = {};

// ===== Preview / Cámara =====
let qrAutoScanTimer = null;

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('✨ Lab Control MVP Iniciado');
    cargarEstados();
    setInterval(cargarEstados, 5000); // Actualizar cada 5s
    updateClock();
    setInterval(updateClock, 1000);
});

// ==================== CÁMARA PREVIEW (QR) ====================

function startCameraPreview() {
    const img = document.getElementById('camera-preview');
    if (!img) return;

    // Inicia MJPEG stream desde backend
    img.src = '/api/camera_feed';
    img.style.display = 'block';
}

function stopCameraPreview() {
    const img = document.getElementById('camera-preview');
    if (!img) return;

    // Detiene MJPEG stream (libera cámara del lado navegador)
    img.src = '';
    img.style.display = 'none';
}

function clearQrAutoScanTimer() {
    if (qrAutoScanTimer) {
        clearTimeout(qrAutoScanTimer);
        qrAutoScanTimer = null;
    }
}

// ==================== CARGAR ESTADOS ====================

async function cargarEstados() {
    try {
        // Primero sincronizar con Laravel
        await fetch('/api/sincronizar', { method: 'POST' });

        // Luego obtener estados locales actualizados
        const response = await fetch('/api/estados');
        const data = await response.json();

        if (data.success) {
            mesasData = data.estados;
            actualizarUI(data.estados);
        }
    } catch (error) {
        console.error('Error cargando estados:', error);
    }
}

function actualizarUI(estados) {
    for (const [id, mesa] of Object.entries(estados)) {
        const mesaElement = document.querySelector(`[data-mesa-id="${id}"]`);
        if (!mesaElement) continue;

        // Actualizar clases
        mesaElement.className = 'mesa-card';

        if (mesa.estado === 'disponible') {
            mesaElement.classList.add('disponible');
        } else if (mesa.estado === 'ocupado') {
            mesaElement.classList.add('ocupado');
        } else if (mesa.estado === 'mantenimiento') {
            mesaElement.classList.add('mantenimiento');
        }
    }
}

// ==================== CLICK EN MESA ====================

function handleMesaClick(mesaId) {
    const mesa = mesasData[mesaId];
    if (!mesa) return;

    currentMesa = mesaId;

    if (mesa.estado === 'disponible') {
        currentAction = 'ocupar';
        document.getElementById('confirm-title').textContent = 'Ocupar Mesa';
        document.getElementById('confirm-message').textContent = `¿Deseas ocupar la Mesa ${mesaId}?`;
    } else if (mesa.estado === 'ocupado') {
        currentAction = 'liberar';
        document.getElementById('confirm-title').textContent = 'Desocupar Mesa';
        document.getElementById('confirm-message').textContent = `¿Deseas desocupar la Mesa ${mesaId}?`;
    } else {
        showToast('Esta mesa no está disponible', 'info');
        return;
    }

    openModal('confirm-modal');
}

function confirmAction() {
    closeModal('confirm-modal');
    openModal('qr-modal');

    document.getElementById('modal-title').textContent =
        currentAction === 'ocupar'
            ? `Acerca tu credencial - Mesa ${currentMesa}`
            : `Confirma tu identidad - Mesa ${currentMesa}`;

    // ✅ Prender preview al abrir modal
    startCameraPreview();

    // ✅ Auto-escanear (si NO lo quieres, comenta estas 3 líneas)
    clearQrAutoScanTimer();
    qrAutoScanTimer = setTimeout(() => {
        escanearQR();
    }, 600);
}

// ==================== TECLADO MANUAL ====================

function showKeyboard() {
    closeModal('qr-modal');
    openModal('keyboard-modal');
    document.getElementById('matricula-input').value = '';
}

function pressKey(number) {
    const input = document.getElementById('matricula-input');
    if (input.value.length < 12) {
        input.value += number;
    }
}

function backspace() {
    const input = document.getElementById('matricula-input');
    input.value = input.value.slice(0, -1);
}

async function submitMatricula() {
    const matricula = document.getElementById('matricula-input').value;

    closeModal('keyboard-modal');

    // Ejecutar acción (ocupar o liberar)
    if (currentAction === 'ocupar') {
        await ocuparMesa(currentMesa, matricula);
    } else if (currentAction === 'liberar') {
        await liberarMesa(currentMesa, matricula);
    }
}

// ==================== ESCANEO QR ====================

async function escanearQR() {
    showToast('Escaneando código QR...', 'info');

    // ⚠️ Importante: detener preview antes de escanear
    // porque el stream y el escaneo pueden pelearse la cámara
    stopCameraPreview();

    try {
        const response = await fetch('/api/escanear_qr', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            closeModal('qr-modal');
            const matricula = data.matricula;

            // Ejecutar acción
            if (currentAction === 'ocupar') {
                await ocuparMesa(currentMesa, matricula);
            } else if (currentAction === 'liberar') {
                await liberarMesa(currentMesa, matricula);
            }
        } else {
            showToast(data.error || 'Error escaneando QR', 'error');

            // Si falló, vuelve a prender preview para que el usuario se acomode
            startCameraPreview();

            // (Opcional) reintentar auto-scan después de un ratito
            clearQrAutoScanTimer();
            qrAutoScanTimer = setTimeout(() => {
                escanearQR();
            }, 1500);
        }
    } catch (error) {
        console.error('Error QR:', error);
        showToast('Error conectando con escáner', 'error');

        // Vuelve a prender preview si hay error de red
        startCameraPreview();
    }
}

// ==================== OCUPAR MESA ====================

async function ocuparMesa(mesaId, matricula) {
    try {
        const response = await fetch('/api/ocupar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mesa_id: parseInt(mesaId),
                matricula: matricula
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.mensaje, 'success');
            cargarEstados(); // Recargar estados
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        console.error('Error ocupando mesa:', error);
        showToast('Error al ocupar mesa', 'error');
    }
}

// ==================== LIBERAR MESA ====================

async function liberarMesa(mesaId, matricula) {
    try {
        const response = await fetch('/api/liberar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mesa_id: parseInt(mesaId),
                matricula: matricula
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.mensaje, 'success');
            cargarEstados(); // Recargar estados
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        console.error('Error liberando mesa:', error);
        showToast('Error al liberar mesa', 'error');
    }
}

// ==================== MODALES ====================

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');

    // ✅ Si se cierra el modal del QR, apagar preview y cancelar reintentos
    if (modalId === 'qr-modal') {
        stopCameraPreview();
        clearQrAutoScanTimer();
    }
}

// ==================== NOTIFICACIONES ====================

function showToast(mensaje, tipo = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = mensaje;
    toast.className = `toast ${tipo} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ==================== RELOJ ====================

function updateClock() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('current-time').textContent =
        now.toLocaleDateString('es-MX', options);
}
