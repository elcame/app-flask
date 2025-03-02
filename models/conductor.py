from extensions import db

class Conductor(db.Model):
    __tablename__ = 'CONDUCTOR'
    ID_CONDUCTOR = db.Column(db.Integer, primary_key=True)
    NOMBRE = db.Column(db.String(100), nullable=False)
    CÉDULA = db.Column(db.String(50), nullable=False)
    NÚMERO_LICENCIA = db.Column(db.String(50), nullable=False)
    FECHA_EXPEDICIÓN_LICENCIA = db.Column(db.Date, nullable=False)
    CELULAR = db.Column(db.String(20), nullable=False)
    ID_EMPRESA = db.Column(db.Integer, db.ForeignKey('EMPRESA.ID_EMPRESA'))

    empresa = db.relationship('Empresa', backref=db.backref('conductores', lazy=True))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}