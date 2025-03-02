from extensions import db

class Tractocamion(db.Model):
    __tablename__ = 'TRACTOCAMION'
    ID_TRACTO = db.Column(db.Integer, primary_key=True)
    MARCA = db.Column(db.String(100), nullable=False)
    MODELO = db.Column(db.String(100), nullable=False)
    PLACA = db.Column(db.String(20), nullable=False)
    ID_EMPRESA = db.Column(db.Integer, db.ForeignKey('EMPRESA.ID_EMPRESA'))

    empresa = db.relationship('Empresa', backref=db.backref('tractocamiones', lazy=True))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}