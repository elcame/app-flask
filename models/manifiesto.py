from extensions import db

class Manifiesto(db.Model):
    __tablename__ = 'MANIFIESTOS'
    
    id = db.Column(db.String(50), primary_key=True)
    numero = db.Column(db.Integer)
    placa = db.Column(db.String(20))
    conductor = db.Column(db.String(100))
    origen = db.Column(db.String(100))
    destino = db.Column(db.String(100))
    fecha = db.Column(db.Date)
    mes = db.Column(db.String(20))
    kof1 = db.Column(db.String(20))
    remesa = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    valor_flete = db.Column(db.Float)

    def __repr__(self):
        return f'<Manifiesto {self.id}>'

    def to_dict(self):
        try:
            # Verificar que tenemos un objeto válido
            if not self:
                raise ValueError("El objeto manifiesto es None")
            
            # Mapeo de meses de inglés a español
            meses = {
                'JANUARY': 'ENERO',
                'FEBRUARY': 'FEBRERO',
                'MARCH': 'MARZO',
                'APRIL': 'ABRIL',
                'MAY': 'MAYO',
                'JUNE': 'JUNIO',
                'JULY': 'JULIO',
                'AUGUST': 'AGOSTO',
                'SEPTEMBER': 'SEPTIEMBRE',
                'OCTOBER': 'OCTUBRE',
                'NOVEMBER': 'NOVIEMBRE',
                'DECEMBER': 'DICIEMBRE'
            }
            
            # Crear el diccionario con todos los campos
            dict_data = {
                'id': str(self.id) if self.id is not None else '',
                'numero': int(self.numero) if self.numero is not None else 0,
                'placa': str(self.placa) if self.placa is not None else '',
                'conductor': str(self.conductor) if self.conductor is not None else '',
                'origen': str(self.origen) if self.origen is not None else '',
                'destino': str(self.destino) if self.destino is not None else '',
                'fecha': self.fecha.strftime('%Y-%m-%d') if self.fecha is not None else '',
                'mes': meses.get(str(self.mes).upper(), str(self.mes)) if self.mes is not None else '',
                'kof': str(self.kof1) if self.kof1 is not None else '',
                'remesa': str(self.remesa) if self.remesa is not None else '',
                'empresa': str(self.empresa) if self.empresa is not None else '',
                'valor_flete': float(self.valor_flete) if self.valor_flete is not None else 0.0
            }
            
            # Verificar que el diccionario no está vacío
            if not dict_data:
                raise ValueError("El diccionario está vacío")
            
            # Verificar que es un diccionario
            if not isinstance(dict_data, dict):
                raise ValueError(f"El resultado no es un diccionario, es {type(dict_data)}")
            
            # Verificar que tenemos todos los campos necesarios
            campos_requeridos = ['id', 'placa', 'conductor', 'origen', 'destino', 'fecha', 'mes', 'kof', 'remesa', 'empresa', 'valor_flete']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in dict_data]
            if campos_faltantes:
                raise ValueError(f"Faltan campos en el diccionario: {campos_faltantes}")
            
            return dict_data
        except Exception as e:
            raise  # Re-lanzar la excepción para que sea manejada por la ruta
           