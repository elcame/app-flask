from extensions import db

class DetallesConductores(db.Model):
    __tablename__ = 'DetallesConductores'
    ID_TRABAJADOR = db.Column(db.Integer, db.ForeignKey('Trabajadores.ID_TRABAJADOR'), primary_key=True)
    FECHA_EXPEDICION_LICENCIA = db.Column(db.Date, nullable=False)
    ID_TRACTO = db.Column(db.Integer, db.ForeignKey('Tractocamion.ID_TRACTO'), nullable=False)

    trabajador = db.relationship('Trabajadores', backref=db.backref('detalles_conductores', uselist=False))
    tractocamion = db.relationship('Tractocamion', backref=db.backref('detalles_conductores', uselist=False))

    def as_dict(self):
        return {
            'ID_TRABAJADOR': self.ID_TRABAJADOR,
            'FECHA_EXPEDICION_LICENCIA': self.FECHA_EXPEDICION_LICENCIA,
            'ID_TRACTO': self.ID_TRACTO
        }