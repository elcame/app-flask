from extensions import db

class Seguro(db.Model):
    __tablename__ = 'seguros'

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), nullable=False)  # Quitamos temporalmente la restricción de clave foránea
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255))
    
    tractocamion = db.relationship('Tractocamion', backref=db.backref('seguros', lazy=True))
    
    
   