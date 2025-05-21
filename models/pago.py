from extensions import db

class Pago(db.Model):
    __tablename__ = 'pagos'

    id_pago = db.Column(db.Integer, primary_key=True)
    tipo_pago = db.Column(db.String(50), nullable=False)  # manifiesto, mantenimiento, seguro, sueldo
    id_referencia = db.Column(db.Integer, nullable=False)  # ID del manifiesto, mantenimiento, etc.
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    placa = db.Column(db.String(50), nullable=False)