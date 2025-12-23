"""
Lab Control MVP - Aplicación Principal
"""
from flask import Flask, render_template, jsonify, request
import logging
from datetime import datetime

from config.settings import HOST, PORT, DEBUG, DATABASE_URI, OPERATING_HOURS, OPERATING_DAYS
from models.database import db, init_db, Mesa, Sesion
from hardware.gpio_control import relay_controller
from hardware.qr_scanner import qr_scanner
from api.laravel_client import laravel_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

print("=" * 60)
print("🔧 LAB CONTROL MVP")
print("=" * 60)

def validar_horario() -> bool:
    now = datetime.now()
    if now.weekday() not in OPERATING_DAYS:
        return False
    current_time = now.time()
    start = datetime.strptime(OPERATING_HOURS['start'], '%H:%M').time()
    end = datetime.strptime(OPERATING_HOURS['end'], '%H:%M').time()
    return start <= current_time <= end

def validar_usuario_sin_mesa(matricula: str) -> bool:
    mesa_activa = Mesa.query.filter_by(usuario_actual=matricula, estado=1).first()
    return mesa_activa is None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/estados', methods=['GET'])
def get_estados():
    mesas = Mesa.query.all()
    estados = {}
    for mesa in mesas:
        estados[str(mesa.id)] = {
            'id': mesa.id,
            'estado': mesa.get_estado_str(),
            'usuario': mesa.usuario_actual,
            'hora_inicio': mesa.hora_inicio.isoformat() if mesa.hora_inicio else None
        }
    return jsonify({
        'success': True,
        'estados': estados,
        'gpio_available': relay_controller.gpio_available,
        'qr_available': qr_scanner.is_available()
    })

@app.route('/api/sincronizar', methods=['POST'])
def sincronizar_con_laravel():
    """Sincroniza estados desde Laravel"""
    try:
        # Obtener mesas desde Laravel
        success, mesas_laravel = laravel_client.obtener_todas_mesas()
        
        if not success:
            return jsonify({'success': False, 'error': 'Error consultando Laravel'}), 500
        
        # Actualizar base de datos local
        for mesa_laravel in mesas_laravel:
            mesa_id = mesa_laravel.get('id')
            mesa_local = Mesa.query.get(mesa_id)
            
            if not mesa_local:
                continue
            
            # Si Laravel dice ocupada pero local dice disponible
            if mesa_laravel.get('Estado') == 1 and mesa_local.estado == 0:
                # Actualizar local
                mesa_local.estado = 1
                mesa_local.usuario_actual = str(mesa_laravel.get('user_id'))
                mesa_local.hora_inicio = datetime.now()
                
            # Si Laravel dice disponible pero local dice ocupada
            elif mesa_laravel.get('Estado') == 0 and mesa_local.estado == 1:
                # Liberar local
                mesa_local.liberar()
        
        db.session.commit()
        
        return jsonify({'success': True, 'mensaje': 'Sincronizado correctamente'})
    
    except Exception as e:
        logger.error(f"Error sincronizando: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ocupar', methods=['POST'])
def ocupar_mesa():
    try:
        data = request.json
        mesa_id = int(data['mesa_id'])
        matricula = str(data['matricula'])
        
        if not validar_horario():
            return jsonify({'success': False, 'error': 'Fuera de horario'}), 400
        
        if not validar_usuario_sin_mesa(matricula):
            return jsonify({'success': False, 'error': 'Ya tienes otra mesa activa'}), 400
        
        success, mensaje = laravel_client.iniciar_espacio(mesa_id, matricula)
        if not success:
            return jsonify({'success': False, 'error': mensaje}), 400
        
        mesa = Mesa.query.get(mesa_id)
        if not mesa:
            return jsonify({'success': False, 'error': 'Mesa no existe'}), 404
        
        mesa.ocupar(matricula)
        sesion = Sesion(mesa_id=mesa_id, matricula=matricula, hora_inicio=datetime.now())
        db.session.add(sesion)
        db.session.commit()
        
        relay_controller.turn_on(mesa_id)
        
        return jsonify({
            'success': True,
            'mensaje': f'Mesa {mesa_id} ocupada exitosamente',
            'mesa': {'id': mesa.id, 'estado': mesa.get_estado_str(), 'usuario': mesa.usuario_actual}
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/liberar', methods=['POST'])
def liberar_mesa():
    try:
        data = request.json
        mesa_id = int(data['mesa_id'])
        matricula = str(data['matricula'])
        
        mesa = Mesa.query.get(mesa_id)
        if not mesa:
            return jsonify({'success': False, 'error': 'Mesa no existe'}), 404
        
        if mesa.estado != 1:
            return jsonify({'success': False, 'error': 'Mesa no ocupada'}), 400
        
        if mesa.usuario_actual != matricula:
            return jsonify({'success': False, 'error': 'Mesa no te pertenece'}), 400
        
        success, mensaje = laravel_client.finalizar_espacio(mesa_id, matricula)
        if not success:
            return jsonify({'success': False, 'error': mensaje}), 400
        
        mesa.liberar()
        sesion = Sesion.query.filter_by(mesa_id=mesa_id, matricula=matricula, hora_fin=None).first()
        if sesion:
            sesion.finalizar()
        db.session.commit()
        
        relay_controller.turn_off(mesa_id)
        
        return jsonify({
            'success': True,
            'mensaje': f'Mesa {mesa_id} liberada exitosamente',
            'mesa': {'id': mesa.id, 'estado': mesa.get_estado_str()}
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/escanear_qr', methods=['POST'])
def escanear_qr():
    if not qr_scanner.is_available():
        return jsonify({'success': False, 'error': 'Escáner no disponible'}), 503
    success, result = qr_scanner.scan()
    if success:
        return jsonify({'success': True, 'matricula': result})
    else:
        return jsonify({'success': False, 'error': result}), 400

if __name__ == '__main__':
    try:
        print(f"\n✓ Servidor: http://{HOST}:{PORT}\n")
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("\n⚠ Deteniendo...")
    finally:
        relay_controller.cleanup()
        print("✓ Sistema cerrado")
