from extensions import db

class Manifiesto(db.Model):
    __tablename__ = 'MANIFIESTOS'
    
    id = db.Column(db.String(20), primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    placa = db.Column(db.String(10), nullable=False)
    conductor = db.Column(db.String(100), nullable=False)
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    mes = db.Column(db.String(20), nullable=False)
    kof1 = db.Column(db.String(20), nullable=False)
    remesa = db.Column(db.String(20), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    valor_flete = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {
            'id': str(self.id),
            'numero': self.numero,
            'placa': self.placa,
            'conductor': self.conductor,
            'origen': self.origen,
            'destino': self.destino,
            'fecha': self.fecha.strftime('%Y-%m-%d') if self.fecha else None,
            'mes': self.mes,
            'kof1': self.kof1,
            'remesa': self.remesa,
            'empresa': self.empresa,
            'valor_flete': self.valor_flete
        }
           