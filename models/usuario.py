from extensions import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuario'
    ID_USUARIO = db.Column(db.Integer, primary_key=True)
    NOMBRE = db.Column(db.String(50), nullable=False)
    EMAIL = db.Column(db.String(100), unique=True, nullable=False)
    CONTRASEÑA = db.Column(db.String(100), nullable=False)
    TIPO_USUARIO = db.Column(db.String(50), nullable=False)
    ID_EMPRESA = db.Column(db.Integer, db.ForeignKey('Empresa.ID_EMPRESA'), nullable=True)

    def get_id(self):
        return str(self.ID_USUARIO)

    def as_dict(self):
        return {
            'ID_USUARIO': self.ID_USUARIO,
            'NOMBRE': self.NOMBRE,
            'EMAIL': self.EMAIL,
            'CONTRASEÑA': self.CONTRASEÑA,
            'TIPO_USUARIO': self.TIPO_USUARIO,
            'ID_EMPRESA': self.ID_EMPRESA
        }