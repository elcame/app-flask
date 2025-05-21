from extensions import db

class Mantenimiento(db.Model):
    __tablename__ = 'mantenimiento'

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    taller = db.Column(db.String(100))
    km_actual = db.Column(db.Integer)
    proximo_km = db.Column(db.Integer)
    observaciones = db.Column(db.Text)

class MantenimientoRepuestos(db.Model):
    __tablename__ = 'mantenimiento_repuestos'

    id = db.Column(db.Integer, primary_key=True)
    id_mantenimiento = db.Column(db.Integer, db.ForeignKey('mantenimiento.id'), nullable=False)
    repuesto = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)