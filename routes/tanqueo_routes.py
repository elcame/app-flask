from flask import Blueprint, request, jsonify, render_template
from extensions import db
from models.tanqueo import Tanqueo
from models.manifiesto import Manifiesto  # Asegúrate de importar el modelo Manifiesto
from models.pago import Pago  # Asegúrate de importar el modelo Pago

tanqueo_bp = Blueprint('tanqueo_bp', __name__)

@tanqueo_bp.route('/tanqueospost', methods=['POST'])
@tanqueo_bp.route('/tanqueospost', methods=['POST'])
def registrar_tanqueo():
    data = request.get_json()
    try:
        # Validar que la placa y la fecha estén presentes
        if not data.get('placa') or not data.get('fecha'):
            return jsonify({'error': 'La placa y la fecha son obligatorias'}), 400

        # Calcular el número de viajes
        ultimo_tanqueo = Tanqueo.query.filter_by(placa=data['placa']).order_by(Tanqueo.fecha.desc()).first()
        fecha_inicio = ultimo_tanqueo.fecha if ultimo_tanqueo else None
        fecha_ingresada = data['fecha']

        if fecha_inicio:
            numero_viajes = Manifiesto.query.filter(
                Manifiesto.placa == data['placa'],
                Manifiesto.fecha > fecha_inicio,
                Manifiesto.fecha <= fecha_ingresada
            ).count()
        else:
            numero_viajes = Manifiesto.query.filter(
                Manifiesto.placa == data['placa'],
                Manifiesto.fecha <= fecha_ingresada
            ).count()

        # Crear un nuevo tanqueo
        nuevo_tanqueo = Tanqueo(
            placa=data['placa'],
            fecha=data['fecha'],
            galones=data['galones'],
            valor=data['valor'],
            numero_viajes=numero_viajes
        )
        db.session.add(nuevo_tanqueo)
        db.session.flush()  # Obtener el ID del tanqueo antes de confirmar la transacción

        # Crear un registro en la tabla de pagos
        nuevo_pago = Pago(
            tipo_pago='tanqueo',
            id_referencia=nuevo_tanqueo.id,
            monto=data['valor'],
            fecha_pago=data['fecha'],
            placa=data['placa']
        )
        db.session.add(nuevo_pago)

        # Confirmar los cambios en la base de datos
        db.session.commit()

        return jsonify({'message': 'Tanqueo y pago registrados correctamente', 'numero_viajes': numero_viajes}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar el tanqueo: {e}")
        # Manejar errores y devolver un mensaje de error
        
        return jsonify({'error': str(e)}), 500

@tanqueo_bp.route('/tanqueos', methods=['GET'])
def ver_tanqueos():
    # Obtener todos los tanqueos de la base de datos
    tanqueos = Tanqueo.query.all()
    return render_template('tanqueo.html', tanqueos=tanqueos)

@tanqueo_bp.route('/tanqueos', methods=['DELETE'])
def eliminar_todos_tanqueos():
    try:
        # Eliminar los pagos relacionados con tanqueos
        db.session.query(Pago).filter(Pago.tipo_pago == 'tanqueo').delete()
        # Eliminar todos los registros de la tabla tanqueos
        Tanqueo.query.delete()
        db.session.commit()
        return jsonify({'message': 'Todos los tanqueos y sus pagos relacionados han sido eliminados correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tanqueo_bp.route('/tanqueos/<int:id>', methods=['DELETE'])
def eliminar_tanqueo(id):
    try:
        tanqueo = Tanqueo.query.get(id)
        if not tanqueo:
            return jsonify({'error': 'Tanqueo no encontrado'}), 404

        # Eliminar el pago relacionado con este tanqueo
        Pago.query.filter_by(id_referencia=id, tipo_pago='tanqueo').delete()
        db.session.delete(tanqueo)
        db.session.commit()
        return jsonify({'message': f'Tanqueo con ID {id} y su pago relacionado han sido eliminados correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500