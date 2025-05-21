from extensions import db

class DetallesAdministrativos(db.Model):
    __tablename__ = 'DetallesAdministrativos'
    ID_TRABAJADOR = db.Column(db.Integer, db.ForeignKey('Trabajadores.ID_TRABAJADOR'), primary_key=True)
    DEPARTAMENTO = db.Column(db.String(100), nullable=False)

    trabajador = db.relationship('Trabajadores', backref=db.backref('detalles_administrativos', uselist=False))

    def as_dict(self):
        return {
            'ID_TRABAJADOR': self.ID_TRABAJADOR,
            'DEPARTAMENTO': self.DEPARTAMENTO
        }