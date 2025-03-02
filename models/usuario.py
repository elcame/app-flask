from extensions import db

class Usuario(db.Model):
    __tablename__ = 'USUARIOS'
    ID_USUARIO = db.Column(db.Integer, primary_key=True)
    NOMBRE = db.Column(db.String(100), nullable=False)
    EMAIL = db.Column(db.String(100), unique=True, nullable=False)
    CONTRASEÑA = db.Column(db.String(255), nullable=False)
    TIPO_USUARIO = db.Column(db.Enum('ADMINISTRADOR', 'EMPRESA', 'CONDUCTOR'), nullable=False)
    ID_EMPRESA = db.Column(db.Integer, db.ForeignKey('EMPRESA.ID_EMPRESA'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}