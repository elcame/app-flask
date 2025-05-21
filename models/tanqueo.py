from extensions import db

class Tanqueo(db.Model):
    __tablename__ = 'tanqueos'

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    galones = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    numero_viajes = db.Column(db.Integer, nullable=False)