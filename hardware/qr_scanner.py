"""
Escáner QR - Cámara USB
"""
import logging
import time
from config.settings import CAMERA_INDEX, QR_TIMEOUT

logger = logging.getLogger(__name__)

# Intentar importar OpenCV y pyzbar
try:
    import cv2
    from pyzbar import pyzbar
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    logger.warning("⚠ OpenCV/pyzbar no disponible - QR deshabilitado")


class QRScanner:
    """Escáner de códigos QR con cámara USB"""
    
    def __init__(self):
        self.available = SCANNER_AVAILABLE
        self.camera_index = CAMERA_INDEX
        self.timeout = QR_TIMEOUT
    
    def scan(self) -> tuple[bool, str]:
        """
        Escanea código QR desde cámara
        
        Returns:
            (success, matricula_or_error)
        """
        if not self.available:
            logger.error("Escáner QR no disponible")
            return False, "Escáner no disponible"
        
        cap = None
        try:
            # Abrir cámara
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                logger.error(f"No se pudo abrir cámara {self.camera_index}")
                return False, "Cámara no disponible"
            
            logger.info(f"Escaneando QR (timeout {self.timeout}s)...")
            start_time = time.time()
            
            while True:
                # Timeout
                if time.time() - start_time > self.timeout:
                    logger.warning("Timeout escaneando QR")
                    return False, "Timeout - No se detectó QR"
                
                # Leer frame
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Buscar códigos QR
                barcodes = pyzbar.decode(frame)
                
                for barcode in barcodes:
                    # Decodificar
                    barcode_data = barcode.data.decode('utf-8')
                    logger.info(f"✓ QR detectado: {barcode_data}")
                    
                    # Validar que sea numérico (matrícula)
                    if barcode_data.isdigit():
                        return True, barcode_data
                    else:
                        logger.warning(f"QR inválido (no numérico): {barcode_data}")
                        return False, "Código QR inválido"
                
                # Pequeña pausa para no saturar CPU
                time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error escaneando QR: {e}")
            return False, str(e)
        
        finally:
            if cap:
                cap.release()
    
    def is_available(self) -> bool:
        """Verifica si el escáner está disponible"""
        return self.available


# Instancia global
qr_scanner = QRScanner()