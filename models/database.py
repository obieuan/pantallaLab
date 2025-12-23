"""
Modelos de Base de Datos - SQLite
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Mesa(db.Model):
    """Tabla de mesas - Estado actual"""
    __tablename__ = 'mesas'
    
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.Integer, default=0)  # 0=disponible, 1=ocupado, 2=mantenimiento
    usuario_actual = db.Column(db.String(20), nullable=True)
    hora_inicio = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Mesa {self.id}: {self.get_estado_str()}>'
    
    def get_estado_str(self):
        """Retorna estado como string"""
        estados = {0: 'disponible', 1: 'ocupado', 2: 'mantenimiento'}
        return estados.get(self.estado, 'desconocido')
    
    def ocupar(self, matricula):
        """Marca mesa como ocupada"""
        self.estado = 1
        self.usuario_actual = matricula
        self.hora_inicio = datetime.now()
    
    def liberar(self):
        """Marca mesa como disponible"""
        self.estado = 0
        self.usuario_actual = None
        self.hora_inicio = None


class Sesion(db.Model):
    """Historial de sesiones - Para estadísticas"""
    __tablename__ = 'sesiones'
    
    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, nullable=False)
    matricula = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.DateTime, nullable=False)
    hora_fin = db.Column(db.DateTime, nullable=True)
    duracion_minutos = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<Sesion Mesa{self.mesa_id} - {self.matricula}>'
    
    def finalizar(self):
        """Calcula duración al finalizar sesión"""
        self.hora_fin = datetime.now()
        if self.hora_inicio:
            delta = self.hora_fin - self.hora_inicio
            self.duracion_minutos = int(delta.total_seconds() / 60)


def init_db(app):
    """Inicializa base de datos y crea tablas"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Crear 16 mesas si no existen
        if Mesa.query.count() == 0:
            for i in range(1, 17):
                mesa = Mesa(id=i, estado=0)
                db.session.add(mesa)
            db.session.commit()
            print("✓ 16 mesas creadas en base de datos")