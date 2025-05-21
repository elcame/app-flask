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
        return jsonify([manifiesto.as_dict() for manifiesto in manifiestos]), 200
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

@manifiesto_bp.route('/manifiestos/<string:id>', methods=['DELETE'])
def delete_manifiesto(id):
    manifiesto = Manifiesto.query.get(id)
    if manifiesto:
        db.session.delete(manifiesto)
        db.session.commit()
        return jsonify({'message': 'Manifiesto deleted!'}), 200
    else:
        return jsonify({'message': 'Manifiesto not found'}), 404


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


@manifiesto_bp.route('/manifiestos/<int:id>', methods=['PUT'])
def actualizar_manifiesto(id):
    data = request.get_json()
    try:
        manifiesto = Manifiesto.query.get(id)
        if not manifiesto:
            return jsonify({'error': 'Manifiesto no encontrado'}), 404

        # Actualizar los campos del manifiesto
        manifiesto.placa = data.get('placa', manifiesto.placa)
        manifiesto.conductor = data.get('conductor', manifiesto.conductor)
        manifiesto.origen = data.get('origen', manifiesto.origen)
        manifiesto.destino = data.get('destino', manifiesto.destino)
        manifiesto.fecha = data.get('fecha', manifiesto.fecha)
        manifiesto.mes = data.get('mes', manifiesto.mes)
        manifiesto.kof1 = data.get('kof1', manifiesto.kof1)
        manifiesto.remesa = data.get('remesa', manifiesto.remesa)
        manifiesto.empresa = data.get('empresa', manifiesto.empresa)
        manifiesto.valor_flete = data.get('valor_flete', manifiesto.valor_flete)

        db.session.commit()
        return jsonify({'message': 'Manifiesto actualizado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


@manifiesto_bp.route('/manifiestos/<string:placa>', methods=['GET'])
def obtener_manifiestos_por_placa(placa):
    try:
        # Filtrar manifiestos por placa
        manifiestos = Manifiesto.query.filter_by(placa=placa).all()
        print(f"Manifiestos encontrados: {len(manifiestos)}")
        return jsonify([manifiesto.as_dict() for manifiesto in manifiestos]), 200
    except Exception as e:
        print(f"Error al obtener manifiestos por placa: {e}")
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/manifiestos/trabajador/<string:conductor>', methods=['GET'])
def obtener_manifiestos_por_trabajador(conductor):
    try:
        # Filtrar manifiestos por conductor
        manifiestos = Manifiesto.query.filter_by(conductor=conductor).all()
        return jsonify([manifiesto.as_dict() for manifiesto in manifiestos]), 200
    except Exception as e:
        print(f"Error al obtener manifiestos por trabajador: {e}")
        return jsonify({'error': str(e)}), 500

@manifiesto_bp.route('/manifiestos/<int:id>', methods=['GET'])
def get_manifiesto(id):
    manifiesto = Manifiesto.query.get(id)
    if not manifiesto:
        return jsonify({'error': 'Manifiesto no encontrado'}), 404
    return jsonify(manifiesto.as_dict()), 200

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
            'manifiestos': [m.as_dict() for m in manifiestos],
            'total_valor_flete': total_valor_flete
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error al filtrar manifiestos: {str(e)}")
        return jsonify({'error': str(e)}), 500

