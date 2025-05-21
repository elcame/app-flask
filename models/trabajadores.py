from extensions import db
from models.tipo_trabajador import TipoTrabajador

class Trabajadores(db.Model):
    __tablename__ = 'Trabajadores'
    ID_TRABAJADOR = db.Column(db.Integer, primary_key=True)
    NOMBRE = db.Column(db.String(100), nullable=False)
    CEDULA = db.Column(db.String(50), nullable=False)
    FECHA_DE_PAGO = db.Column(db.Date, nullable=False)
    SUELDO = db.Column(db.Numeric(10, 2), nullable=False)
    ID_TIPO = db.Column(db.Integer, db.ForeignKey('TipoTrabajador.ID_TIPO'), nullable=False)
    ID_EMPRESA = db.Column(db.Integer, db.ForeignKey('Empresa.ID_EMPRESA'), nullable=False)

    tipo_trabajador = db.relationship('TipoTrabajador', backref=db.backref('trabajadores', lazy=True))
    empresa = db.relationship('Empresa', backref=db.backref('trabajadores', lazy=True))

    def as_dict(self):
        return {
            'ID_TRABAJADOR': self.ID_TRABAJADOR,
            'NOMBRE': self.NOMBRE,
            'CEDULA': self.CEDULA,
            'FECHA_DE_PAGO': self.FECHA_DE_PAGO,
            'SUELDO': self.SUELDO,
            'ID_TIPO': self.ID_TIPO,
            'ID_EMPRESA': self.ID_EMPRESA
        }