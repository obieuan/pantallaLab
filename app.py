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
        logger.info("Iniciando sincronización con Laravel...")
        
        # Obtener mesas desde Laravel
        success, mesas_laravel = laravel_client.obtener_todas_mesas()
        
        if not success:
            logger.error("Error consultando Laravel")
            return jsonify({'success': False, 'error': 'Error consultando Laravel'}), 500
        
        logger.info(f"Recibidas {len(mesas_laravel)} mesas de Laravel")
        
        # Actualizar base de datos local
        actualizadas = 0
        for mesa_laravel in mesas_laravel:
            mesa_id = mesa_laravel.get('id')
            
            if not mesa_id or mesa_id < 1 or mesa_id > 16:
                continue
            
            mesa_local = Mesa.query.get(mesa_id)
            
            if not mesa_local:
                logger.warning(f"Mesa {mesa_id} no existe en DB local")
                continue
            
            estado_laravel = mesa_laravel.get('Estado', 0)
            user_id_laravel = mesa_laravel.get('user_id')
            
            # Si Laravel dice ocupada (Estado=1) pero local está disponible
            if estado_laravel == 1 and mesa_local.estado != 1:
                logger.info(f"Sincronizando Mesa {mesa_id}: ocupada por user_id {user_id_laravel}")
                mesa_local.estado = 1
                mesa_local.usuario_actual = str(user_id_laravel) if user_id_laravel else None
                mesa_local.hora_inicio = datetime.now()
                
                # ← AGREGAR: Encender GPIO
                relay_controller.turn_on(mesa_id)
                
                actualizadas += 1
                
            # Si Laravel dice disponible (Estado=0) pero local está ocupada
            elif estado_laravel == 0 and mesa_local.estado != 0:
                logger.info(f"Sincronizando Mesa {mesa_id}: liberada")
                mesa_local.liberar()
                
                # ← AGREGAR: Apagar GPIO
                relay_controller.turn_off(mesa_id)
                
                actualizadas += 1
        
        db.session.commit()
        logger.info(f"Sincronización completa: {actualizadas} mesas actualizadas")
        
        return jsonify({
            'success': True, 
            'mensaje': f'{actualizadas} mesas sincronizadas'
        })
    
    except Exception as e:
        logger.error(f"Error sincronizando: {e}", exc_info=True)
        db.session.rollback()
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
        
        logger.info(f"Intentando liberar Mesa {mesa_id} - {matricula}")
        
        # 1. Obtener mesa
        mesa = Mesa.query.get(mesa_id)
        if not mesa:
            return jsonify({'success': False, 'error': 'Mesa no existe'}), 404
        
        # 2. Validar que mesa esté ocupada
        if mesa.estado != 1:
            return jsonify({'success': False, 'error': 'La mesa no está ocupada'}), 400
        
        # 3. Obtener user_id de la matrícula desde Laravel
        success_info, info_alumno = laravel_client.obtener_info_alumno(matricula)
        
        user_id_actual = None
        if success_info:
            # Laravel devuelve el objeto completo del alumno
            user_id_actual = str(info_alumno.get('id')) if isinstance(info_alumno, dict) else None
        
        # 4. Validar que la mesa pertenezca a este usuario
        # Puede estar guardado como user_id o como matrícula
        if mesa.usuario_actual != matricula and mesa.usuario_actual != user_id_actual:
            logger.warning(f"Mesa ocupada por '{mesa.usuario_actual}', intenta liberar '{matricula}' (user_id: {user_id_actual})")
            return jsonify({'success': False, 'error': 'Esta mesa no te pertenece'}), 400
        
        # 5. Validar con API Laravel
        success, mensaje = laravel_client.finalizar_espacio(mesa_id, matricula)
        if not success:
            return jsonify({'success': False, 'error': mensaje}), 400
        
        # 6. Actualizar base de datos local
        mesa.liberar()
        
        # Finalizar sesión activa
        sesion = Sesion.query.filter_by(
            mesa_id=mesa_id,
            matricula=matricula,
            hora_fin=None
        ).first()
        
        if sesion:
            sesion.finalizar()
        
        db.session.commit()
        
        # 7. Apagar GPIO
        relay_controller.turn_off(mesa_id)
        
        logger.info(f"✓ Mesa {mesa_id} liberada exitosamente")
        
        return jsonify({
            'success': True,
            'mensaje': f'Mesa {mesa_id} liberada exitosamente',
            'mesa': {'id': mesa.id, 'estado': mesa.get_estado_str()}
        })
    
    except KeyError as e:
        return jsonify({'success': False, 'error': f'Campo faltante: {e}'}), 400
    except Exception as e:
        logger.error(f"Error liberando mesa: {e}")
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
    
def sincronizar_inicial():
    """Sincronización inicial al arrancar el servidor"""
    logger.info("=" * 60)
    logger.info("Sincronización inicial con Laravel...")
    logger.info("=" * 60)
    
    try:
        with app.app_context():
            # Obtener mesas desde Laravel
            success, mesas_laravel = laravel_client.obtener_todas_mesas()
            
            if not success:
                logger.error("⚠ No se pudo sincronizar con Laravel al inicio")
                return
            
            # Actualizar TODAS las mesas según Laravel
            for mesa_laravel in mesas_laravel:
                mesa_id = mesa_laravel.get('id')
                
                if not mesa_id or mesa_id < 1 or mesa_id > 16:
                    continue
                
                mesa_local = Mesa.query.get(mesa_id)
                if not mesa_local:
                    continue
                
                estado_laravel = mesa_laravel.get('Estado', 0)
                user_id_laravel = mesa_laravel.get('user_id')
                
                # Forzar actualización según Laravel
                if estado_laravel == 1:
                    # Laravel dice ocupada
                    logger.info(f"Mesa {mesa_id}: ocupada (user {user_id_laravel})")
                    mesa_local.estado = 1
                    mesa_local.usuario_actual = str(user_id_laravel) if user_id_laravel else None
                    mesa_local.hora_inicio = datetime.now()
                    relay_controller.turn_on(mesa_id)
                else:
                    # Laravel dice disponible
                    logger.info(f"Mesa {mesa_id}: disponible")
                    mesa_local.liberar()
                    relay_controller.turn_off(mesa_id)
            
            db.session.commit()
            logger.info("✓ Sincronización inicial completada")
            logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Error en sincronización inicial: {e}")

if __name__ == '__main__':
    try:
        # Sincronización inicial
        sincronizar_inicial()
        
        print(f"\n✓ Servidor iniciado en http://{HOST}:{PORT}")
        print("Presiona Ctrl+C para detener\n")
        app.run(host=HOST, port=PORT, debug=DEBUG)
    
    except KeyboardInterrupt:
        print("\n\n⚠ Deteniendo servidor...")
    
    finally:
        relay_controller.cleanup()
        print("✓ Sistema cerrado correctamente")