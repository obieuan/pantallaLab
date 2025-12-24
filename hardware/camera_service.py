import threading
import time
import logging

import cv2

logger = logging.getLogger(__name__)

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except Exception:
    PYZBAR_AVAILABLE = False


class CameraService:
    """
    Mantiene UNA sola instancia de cámara abierta.
    - Lee frames continuamente en un thread.
    - Guarda el último frame.
    - Decodifica QR sobre el frame actual (cada N frames) y guarda el último QR numérico detectado.
    """

    def __init__(self, camera_index: int = 0, decode_every_n_frames: int = 3):
        self.camera_index = camera_index
        self.decode_every_n_frames = max(1, int(decode_every_n_frames))

        self._cap = None
        self._thread = None
        self._stop_event = threading.Event()

        self._lock = threading.Lock()
        self._last_frame = None  # frame BGR
        self._last_jpeg = None   # bytes jpg

        self._last_qr = None
        self._last_qr_ts = None

        self._frame_count = 0
        self._running = False

    def start(self) -> bool:
        if self._running:
            return True

        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            logger.error(f"No se pudo abrir cámara {self.camera_index}")
            self._cap.release()
            self._cap = None
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._running = True
        logger.info(f"✓ CameraService iniciado (index={self.camera_index})")
        return True

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass

        self._cap = None
        self._thread = None
        self._running = False
        logger.info("CameraService detenido")

    def is_running(self) -> bool:
        return self._running and (self._cap is not None)

    def get_jpeg(self) -> bytes | None:
        with self._lock:
            return self._last_jpeg

    def consume_last_qr(self) -> str | None:
        """
        Devuelve el último QR detectado (solo numérico) y lo limpia,
        para que no lo “re-leas” infinito.
        """
        with self._lock:
            qr = self._last_qr
            self._last_qr = None
            self._last_qr_ts = None
            return qr

    def peek_last_qr(self) -> tuple[str | None, float | None]:
        with self._lock:
            return self._last_qr, self._last_qr_ts

    def _loop(self):
        while not self._stop_event.is_set():
            ret, frame = self._cap.read()
            if not ret:
                time.sleep(0.02)
                continue

            self._frame_count += 1

            # Guardar frame + jpg
            ok, buffer = cv2.imencode(".jpg", frame)
            if ok:
                jpg = buffer.tobytes()
                with self._lock:
                    self._last_frame = frame
                    self._last_jpeg = jpg

            # Decodificar QR cada N frames (reduce CPU)
            if PYZBAR_AVAILABLE and (self._frame_count % self.decode_every_n_frames == 0):
                try:
                    barcodes = pyzbar.decode(frame)
                    for b in barcodes:
                        data = b.data.decode("utf-8", errors="ignore").strip()
                        # Solo matrícula numérica
                        if data.isdigit():
                            with self._lock:
                                self._last_qr = data
                                self._last_qr_ts = time.time()
                            logger.info(f"✓ QR detectado: {data}")
                            break
                except Exception as e:
                    logger.warning(f"Error decodificando QR: {e}")

            time.sleep(0.01)
