from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app
from extensions import db
from models.manifiesto import Manifiesto
import os


manifiesto_bp = Blueprint('manifiesto_bp', __name__)
@manifiesto_bp.route('/obtenermanifiestos', methods=['GET'])
def obtener_manifiestos():
    try:
        print("Obteniendo todos los manifiestos")
        manifiestos = Manifiesto.query.all()
        return jsonify([manifiesto.to_dict() for manifiesto in manifiestos]), 200
    except Exception as e:
        print(f"Error al obtener manifiestos: {e}")
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/manifiestos', methods=['POST'])
def add_manifiesto():
    try:
        data = request.get_json()
        new_manifiesto = Manifiesto(
           
            numero=data['NUMERO'],
            placa=data['PLACA'],
            conductor=data['CONDUCTOR'],
            origen=data['ORIGEN'],
            destino=data['DESTINO'],
            fecha=data['FECHA'],
            mes=data['MES'],
            id=data['ID'],
            kof1=data['KOF'],
            remesa=data['REMESA'],
            empresa=data['EMPRESA'],
            valor_flete=data['VALOR_FLETE']
        )
        db.session.add(new_manifiesto)
        db.session.commit()
        return jsonify({'message': 'Manifiesto added!', 'id': new_manifiesto.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'data': data}), 500

@manifiesto_bp.route('/manifiestos/<id>', methods=['DELETE'])
def delete_manifiesto(id):
    try:
        # Convertir el ID a string ya que en la base de datos es character varying
        manifiesto = Manifiesto.query.get(str(id))
        if not manifiesto:
            return jsonify({'error': 'Manifiesto no encontrado'}), 404
            
        db.session.delete(manifiesto)
        db.session.commit()
        return jsonify({'message': 'Manifiesto eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar manifiesto: {str(e)}")
        return jsonify({'error': str(e)}), 500


@manifiesto_bp.route('/manifiestos/eliminar_todos', methods=['DELETE'])
def eliminar_todos_manifiestos():
    try:
        # Eliminar todos los registros de la tabla manifiesto
        db.session.query(Manifiesto).delete()
        db.session.commit()
        return jsonify({'message': 'Todos los manifiestos han sido eliminados correctamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@manifiesto_bp.route('/manifiestos/<id>', methods=['PUT'])
def update_manifiesto(id):
    try:
        # Convertir el ID a string ya que en la base de datos es character varying
        id_str = str(id)
        manifiesto = Manifiesto.query.filter(Manifiesto.id == id_str).first()
        if not manifiesto:
            return jsonify({'error': 'Manifiesto no encontrado'}), 404
            
        data = request.get_json()
        
        # Mapeo de meses de español a inglés
        meses = {
            'ENERO': 'JANUARY',
            'FEBRERO': 'FEBRUARY',
            'MARZO': 'MARCH',
            'ABRIL': 'APRIL',
            'MAYO': 'MAY',
            'JUNIO': 'JUNE',
            'JULIO': 'JULY',
            'AGOSTO': 'AUGUST',
            'SEPTIEMBRE': 'SEPTEMBER',
            'OCTUBRE': 'OCTOBER',
            'NOVIEMBRE': 'NOVEMBER',
            'DICIEMBRE': 'DECEMBER'
        }
        
        # Mapeo de campos en minúsculas a campos del modelo
        mapeo_campos = {
            'id': 'id',
            'placa': 'placa',
            'conductor': 'conductor',
            'origen': 'origen',
            'destino': 'destino',
            'fecha': 'fecha',
            'mes': 'mes',
            'kof': 'kof1',
            'remesa': 'remesa',
            'empresa': 'empresa',
            'valor_flete': 'valor_flete'
        }
        
        # Actualizar cada campo
        for campo_frontend, campo_modelo in mapeo_campos.items():
            if campo_frontend in data:
                valor = data[campo_frontend]
                # Si es el campo mes, convertir de español a inglés
                if campo_frontend == 'mes':
                    valor = meses.get(valor.upper(), valor)
                setattr(manifiesto, campo_modelo, valor)
            
        db.session.commit()
        return jsonify({'message': 'Manifiesto actualizado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


@manifiesto_bp.route('/manifiestos/<id>', methods=['GET'])
def get_manifiesto(id):
    try:
        # Convertir el ID a string ya que en la base de datos es character varying
        id_str = str(id)
        print(f"Buscando manifiesto con ID: {id_str}")  # Debug
        
        # Obtener el manifiesto usando filter con comparación exacta
        manifiesto = Manifiesto.query.filter(Manifiesto.id == id_str).first()
        print(f"Resultado de la búsqueda: {manifiesto}")  # Debug
        
        if not manifiesto:
            print(f"No se encontró el manifiesto con ID: {id_str}")  # Debug
            return jsonify({'error': 'Manifiesto no encontrado'}), 404
        
        # Convertir a diccionario
        try:
            manifiesto_dict = manifiesto.to_dict()
            print(f"Manifiesto convertido a diccionario: {manifiesto_dict}")  # Debug
            
            # Verificar que el diccionario no esté vacío
            if not manifiesto_dict:
                print("Error: El diccionario está vacío")  # Debug
                return jsonify({'error': 'Error al convertir manifiesto'}), 500
            
            # Verificar que es un diccionario y no una lista
            if isinstance(manifiesto_dict, list):
                print("Error: Se recibió una lista en lugar de un diccionario")  # Debug
                return jsonify({'error': 'Error en el formato de datos'}), 500
            
            # Verificar que tenemos todos los campos necesarios
            campos_requeridos = ['id', 'placa', 'conductor', 'origen', 'destino', 'fecha', 'mes', 'kof', 'remesa', 'empresa', 'valor_flete']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in manifiesto_dict]
            if campos_faltantes:
                print(f"Error: Faltan campos en el diccionario: {campos_faltantes}")  # Debug
                return jsonify({'error': f'Faltan campos en el manifiesto: {campos_faltantes}'}), 500
            
            # Devolver el diccionario directamente
            response = jsonify(manifiesto_dict)
            print(f"Respuesta a enviar: {response.get_data(as_text=True)}")  # Debug
            return response, 200
            
        except Exception as e:
            print(f"Error al convertir manifiesto a diccionario: {str(e)}")  # Debug
            return jsonify({'error': f'Error al convertir manifiesto: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Error al obtener manifiesto: {str(e)}")  # Debug
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/manifiestos/placa/<string:placa>', methods=['GET'])
def obtener_manifiestos_por_placa(placa):
    try:
        # Filtrar manifiestos por placa
        manifiestos = Manifiesto.query.filter_by(placa=placa).all()
        print(f"Manifiestos encontrados para placa {placa}: {len(manifiestos)}")  # Debug
        
        # Si solo hay un manifiesto, devolverlo como objeto
        if len(manifiestos) == 1:
            return jsonify(manifiestos[0].to_dict()), 200
            
        # Si hay múltiples manifiestos, devolver el array
        return jsonify([manifiesto.to_dict() for manifiesto in manifiestos]), 200
    except Exception as e:
        print(f"Error al obtener manifiestos por placa: {e}")
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/manifiestos/trabajador/<string:conductor>', methods=['GET'])
def obtener_manifiestos_por_trabajador(conductor):
    try:
        # Filtrar manifiestos por conductor
        manifiestos = Manifiesto.query.filter_by(conductor=conductor).all()
        return jsonify([manifiesto.to_dict() for manifiesto in manifiestos]), 200
    except Exception as e:
        print(f"Error al obtener manifiestos por trabajador: {e}")
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/excel/<path:subpath>')
def download_excel(subpath):
    try:
        # Dividir la ruta en directorio y archivo
        directory = os.path.dirname(subpath)
        filename = os.path.basename(subpath)
        
        # Construir la ruta completa al directorio
        excel_dir = os.path.join(os.getcwd(), 'excel')
        if directory:
            excel_dir = os.path.join(excel_dir, directory)
        
        # Verificar si el directorio existe
        if not os.path.exists(excel_dir):
            current_app.logger.error(f"Directorio no encontrado: {excel_dir}")
            return jsonify({'error': 'Directorio no encontrado'}), 404
            
        # Verificar si el archivo existe
        file_path = os.path.join(excel_dir, filename)
        if not os.path.exists(file_path):
            current_app.logger.error(f"Archivo no encontrado: {file_path}")
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        current_app.logger.info(f"Sirviendo archivo: {file_path}")
        return send_from_directory(excel_dir, filename)
        
    except Exception as e:
        current_app.logger.error(f"Error al servir archivo Excel: {str(e)}")
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/manifiestos/filtrar', methods=['GET'])
def filtrar_manifiestos():
    try:
        conductor = request.args.get('conductor', '')
        placa = request.args.get('placa', '')
        mes = request.args.get('mes', '')

        query = Manifiesto.query

        if conductor:
            query = query.filter(Manifiesto.conductor == conductor)
        if placa:
            query = query.filter(Manifiesto.placa == placa)
        if mes:
            query = query.filter(Manifiesto.mes == mes)

        manifiestos = query.all()
        
        # Calcular el total del valor flete
        total_valor_flete = sum(float(m.valor_flete or 0) for m in manifiestos)
        
        return jsonify({
            'manifiestos': [m.to_dict() for m in manifiestos],
            'total_valor_flete': total_valor_flete
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error al filtrar manifiestos: {str(e)}")
        return jsonify({'error': str(e)}), 500

