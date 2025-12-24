// Lab Control MVP - Frontend JavaScript
// Conecta con Flask backend

let currentMesa = null;
let currentAction = null;
let mesasData = {};

// ===== Preview / QR live =====
let qrPollInterval = null;

// Evita que se use un QR viejo y controla estado del flujo QR
let qrFlowBusy = false;
let lastQrSeen = null;
let lastQrSeenAt = 0;
const QR_STALE_MS = 1500; // si un QR se detectó hace >1.5s, lo consideramos "viejo" para el siguiente intento

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
    img.src = '/api/camera_feed';
    img.style.display = 'block';
}

function stopCameraPreview() {
    const img = document.getElementById('camera-preview');
    if (!img) return;
    img.src = '';
    img.style.display = 'none';
}

// Feedback visual en el modal QR
function setQrModalStatus(texto, tipo = 'info') {
    // Si tienes un elemento para texto, úsalo.
    // Reusa toast para no obligarte a cambiar HTML.
    // tipo: 'info' | 'success' | 'error'
    showToast(texto, tipo);

    // Si tu HTML tiene algo como <p class="scan-text">..., lo actualizamos también.
    const scanText = document.querySelector('#qr-modal .scan-text');
    if (scanText) scanText.textContent = texto;
}

// Limpia cualquier QR “pegado” localmente al abrir modal
function resetQrFlowState() {
    qrFlowBusy = false;
    lastQrSeen = null;
    lastQrSeenAt = 0;
}

async function consumeQrBackend() {
    // Esto debe llamar a tu endpoint que hace "consume_last_qr"
    // Si aún no lo tienes así, igual sirve para limpiar si lo implementaste como te pasé.
    try {
        await fetch('/api/escanear_qr', { method: 'POST' });
    } catch (e) {
        // Silencioso
    }
}

function startQrPolling() {
    stopQrPolling();
    resetQrFlowState();

    qrPollInterval = setInterval(async () => {
        // Si ya estamos procesando uno, no sigas leyendo
        if (qrFlowBusy) return;

        try {
            const res = await fetch('/api/qr_status', { cache: 'no-store' });
            const data = await res.json();
            if (!data.success) return;

            if (data.qr) {
                const matricula = data.qr;

                // evita rebotes del mismo valor
                if (matricula === lastQrSeen && (Date.now() - lastQrSeenAt) < QR_STALE_MS) return;

                lastQrSeen = matricula;
                lastQrSeenAt = Date.now();
                qrFlowBusy = true;

                // 1) Feedback inmediato
                showToast(`✅ QR detectado: ${matricula}`, 'success');

                // 2) Consumir YA para que no se pegue
                await consumeQrBackend();

                // 3) Cerrar modal INMEDIATO (esto también apaga cámara/polling por tu closeModal)
                closeModal('qr-modal');

                // 4) Mientras valida por internet, muestra mensaje
                showToast('⏳ Validando…', 'info');

                // 5) Ejecutar acción (puede tardar)
                if (currentAction === 'ocupar') {
                    await ocuparMesa(currentMesa, matricula);
                } else if (currentAction === 'liberar') {
                    await liberarMesa(currentMesa, matricula);
                }

                // 6) Reset para siguiente uso
                resetQrFlowState();
            }
        } catch (e) {
            // Si falla, no lo dejes muerto; avisa y sigue intentando
            console.error('qr_status failed', e);
            setQrModalStatus('⚠ Error leyendo cámara/QR. Reintentando...', 'error');
        }
    }, 200); // un poco más rápido para sensación "instantánea"
}

function stopQrPolling() {
    if (qrPollInterval) {
        clearInterval(qrPollInterval);
        qrPollInterval = null;
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

async function confirmAction() {
    closeModal('confirm-modal');
    openModal('qr-modal');

    document.getElementById('modal-title').textContent =
        currentAction === 'ocupar'
            ? `Acerca tu credencial - Mesa ${currentMesa}`
            : `Confirma tu identidad - Mesa ${currentMesa}`;

    // ✅ MUY IMPORTANTE: limpiar backend al abrir para que no agarre un QR viejo
    // (por si quedó uno detectado de hace rato)
    await consumeQrBackend();
    resetQrFlowState();

    setQrModalStatus('Escaneando código QR...', 'info');

    // Preview + escucha QR en vivo
    startCameraPreview();
    startQrPolling();
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

// ==================== ESCANEO QR (compat) ====================
// Ya no es necesario para el modo "BIEN", pero lo dejo por si quieres botón manual.
async function escanearQR() {
    showToast('Escaneando código QR...', 'info');

    try {
        const response = await fetch('/api/escanear_qr', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            closeModal('qr-modal');
            const matricula = data.matricula;

            if (currentAction === 'ocupar') {
                await ocuparMesa(currentMesa, matricula);
            } else if (currentAction === 'liberar') {
                await liberarMesa(currentMesa, matricula);
            }
        } else {
            showToast(data.error || 'Aún no se detecta QR', 'info');
        }
    } catch (error) {
        console.error('Error QR:', error);
        showToast('Error conectando con escáner', 'error');
    }
}

// ==================== OCUPAR MESA ====================

async function ocuparMesa(mesaId, matricula) {
    try {
        const response = await fetch('/api/ocupar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mesa_id: parseInt(mesaId), matricula: matricula })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.mensaje, 'success');
            cargarEstados();
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mesa_id: parseInt(mesaId), matricula: matricula })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.mensaje, 'success');
            cargarEstados();
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

    if (modalId === 'qr-modal') {
        stopQrPolling();
        stopCameraPreview();
        resetQrFlowState();
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
