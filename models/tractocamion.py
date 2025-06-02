from extensions import db

class Tractocamion(db.Model):
    __tablename__ = 'Tractocamion'
    ID_TRACTO = db.Column(db.Integer, primary_key=True)
    MARCA = db.Column(db.String(50), nullable=False)
    MODELO = db.Column(db.String(50), nullable=False)
    PLACA = db.Column(db.String(50), nullable=False, unique=True)
    ID_EMPRESA = db.Column(db.Integer, db.ForeignKey('Empresa.ID_EMPRESA'), nullable=False)

    empresa = db.relationship('Empresa', backref=db.backref('tractocamiones', lazy=True))

    def as_dict(self):
        return {
            'ID_TRACTO': self.ID_TRACTO,
            'MARCA': self.MARCA,
            'MODELO': self.MODELO,
            'PLACA': self.PLACA,
            'ID_EMPRESA': self.ID_EMPRESA
        }