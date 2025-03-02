from extensions import db

class Pago(db.Model):
    __tablename__ = 'PAGO'

    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))

    def __init__(self, monto, metodo_pago, descripcion=None):
        self.monto = monto
        self.metodo_pago = metodo_pago
        self.descripcion = descripcion

    def __repr__(self):
        return f'<Pago {self.id}>'