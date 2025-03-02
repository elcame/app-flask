from extensions import db

class Mantenimiento(db.Model):
    __tablename__ = 'MANTENIMIENTO'
    ID_MANTENIMIENTO = db.Column(db.Integer, primary_key=True)
    DESCRIPCION = db.Column(db.String(255), nullable=False)
    FECHA = db.Column(db.Date, nullable=False)
    COSTO = db.Column(db.Float, nullable=False)
    ID_TRACTO = db.Column(db.Integer, db.ForeignKey('TRACTOCAMION.ID_TRACTO'))

    tractocamion = db.relationship('Tractocamion', backref=db.backref('mantenimientos', lazy=True))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}