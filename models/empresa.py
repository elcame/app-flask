from extensions import db

class Empresa(db.Model):
    __tablename__ = 'Empresa'
    ID_EMPRESA = db.Column(db.Integer, primary_key=True)
    NOMBRE = db.Column(db.String(100), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}