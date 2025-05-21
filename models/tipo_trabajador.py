from extensions import db

class TipoTrabajador(db.Model):
    __tablename__ = 'TipoTrabajador'
    ID_TIPO = db.Column(db.Integer, primary_key=True)
    DESCRIPCION = db.Column(db.String(50), nullable=False)

    def as_dict(self):
        return {
            'ID_TIPO': self.ID_TIPO,
            'DESCRIPCION': self.DESCRIPCION
        }