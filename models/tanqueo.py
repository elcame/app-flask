from extensions import db

class Tanqueo(db.Model):
    __tablename__ = 'TANQUEO'
    ID_TANQUEO = db.Column(db.Integer, primary_key=True)
    ID_CONDUCTOR = db.Column(db.Integer, db.ForeignKey('CONDUCTOR.ID_CONDUCTOR'))
    ID_TRACTO = db.Column(db.Integer, db.ForeignKey('TRACTOCAMION.ID_TRACTO'))
    GALONES = db.Column(db.Float, nullable=False)
    PRECIO_GALON = db.Column(db.Float, nullable=False)
    FECHA = db.Column(db.DateTime, nullable=False)
    TOTAL = db.Column(db.Float, nullable=False)
    ESTACION = db.Column(db.String(100), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}