from extensions import db

class Viajes(db.Model):
    __tablename__ = 'VIAJES'
    ID_VIAJE = db.Column(db.Integer, primary_key=True)
    ORIGEN = db.Column(db.String(100), nullable=False)
    DESTINO = db.Column(db.String(100), nullable=False)
    FECHA_SALIDA = db.Column(db.Date, nullable=False)
    FECHA_LLEGADA = db.Column(db.Date, nullable=False)
    ID_TRACTO = db.Column(db.Integer, db.ForeignKey('TRACTOCAMION.ID_TRACTO'))

    tractocamion = db.relationship('Tractocamion', backref=db.backref('viajes', lazy=True))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}