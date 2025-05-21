from flask import Blueprint, request, jsonify
from extensions import db
from models.tractocamion import Tractocamion
from models.mantenimiento import Mantenimiento, MantenimientoRepuestos
from models.tanqueo import Tanqueo
from models.manifiesto import Manifiesto
from models.pago import Pago
from models.seguro import Seguro
tractocamion_bp = Blueprint('tractocamion_bp', __name__)

@tractocamion_bp.route('/tractocamiones', methods=['GET'])
def get_tractocamiones():
    tractocamiones = Tractocamion.query.all()
    return jsonify([tractocamion.as_dict() for tractocamion in tractocamiones])

@tractocamion_bp.route('/tractocamiones', methods=['POST'])
def add_tractocamion():
    data = None
    try:
        data = request.get_json()
        new_tractocamion = Tractocamion(
            MARCA=data['MARCA'],
            MODELO=data['MODELO'],
            PLACA=data['PLACA'],
            ID_EMPRESA=data['ID_EMPRESA']
        )
        db.session.add(new_tractocamion)
        db.session.commit()
        return jsonify({'message': 'Tractocamion added!', 'ID_TRACTO': new_tractocamion.ID_TRACTO}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'data': data}), 500

@tractocamion_bp.route('/tractocamiones/<int:id>', methods=['DELETE'])
def delete_tractocamion(id):
    tractocamion = Tractocamion.query.get(id)
    if tractocamion:
        db.session.delete(tractocamion)
        db.session.commit()
        return jsonify({'message': 'Tractocamion deleted!'}), 200
    else:
        return jsonify({'message': 'Tractocamion not found'}), 404

@tractocamion_bp.route('/tractocamiones/<int:id>', methods=['PUT'])
def edit_tractocamion(id):
    data = request.get_json()
    tractocamion = Tractocamion.query.get

@tractocamion_bp.route('/tractocamiones/<string:placa>/detalles', methods=['GET'])
def obtener_detalles_tractocamion(placa):
    try:
        # Obtener mantenimientos asociados al tractocamión por placa
        mantenimientos = Mantenimiento.query.filter_by(placa=placa).all()
        mantenimientos_data = [
            {
                'id': mantenimiento.id,
                'fecha': mantenimiento.fecha,
                'valor_total': mantenimiento.valor_total,
                'taller': mantenimiento.taller,
                'observaciones': mantenimiento.observaciones
            }
            for mantenimiento in mantenimientos
        ]

        # Obtener repuestos asociados a los mantenimientos
        repuestos = MantenimientoRepuestos.query.join(Mantenimiento).filter(Mantenimiento.placa == placa).all()
        repuestos_data = [
            {
                'id': repuesto.id,
                'id_mantenimiento': repuesto.id_mantenimiento,
                'nombre': repuesto.repuesto,
                'valor': repuesto.valor,
                'cantidad': repuesto.cantidad,
                'total': repuesto.total
            }
            for repuesto in repuestos
        ]

        # Obtener pagos asociados al tractocamión por placa
        pagos = Pago.query.filter_by(placa=placa).all()
        pagos_data = [
            {
                'id_pago': pago.id_pago,
                'tipo_pago': pago.tipo_pago,
                'id_referencia': pago.id_referencia,
                'monto': pago.monto,
                'fecha_pago': pago.fecha_pago,
                'descripcion': pago.descripcion
            }
            for pago in pagos
        ]

        # Obtener tanqueos asociados al tractocamión por placa
        tanqueos = Tanqueo.query.filter_by(placa=placa).all()
        tanqueos_data = [
            {
                'id': tanqueo.id,
                'fecha': tanqueo.fecha,
                'galones': tanqueo.galones,
                'valor': tanqueo.valor
            }
            for tanqueo in tanqueos
        ]

        return jsonify({
            'mantenimientos': mantenimientos_data,
            'repuestos': repuestos_data,
            'pagos': pagos_data,
            'tanqueos': tanqueos_data
        }), 200
    except Exception as e:
        print(f"Error al obtener detalles del tractocamión: {e}")
        return jsonify({'error': str(e)}), 500
    
@tractocamion_bp.route('/tractocamiones/<string:placa>/pagos', methods=['GET'])
def obtener_pagos_y_estado_seguro(placa):
    try:
        # Obtener todos los pagos asociados a la placa
        pagos = Pago.query.filter_by(placa=placa).all()
        pagos_data = [
            {
                'id_pago': pago.id_pago,
                'placa': pago.placa,
                'tipo_pago': pago.tipo_pago,
                'id_referencia': pago.id_referencia,
                'monto': pago.monto,
                'fecha_pago': pago.fecha_pago,
                'descripcion': pago.descripcion
            }
            for pago in pagos
        ]

        # Verificar si el seguro del mes ya está pagado
        from datetime import datetime
        fecha_actual = datetime.now()
        seguro_pagado = Seguro.query.filter(
            Seguro.placa == placa,
            Seguro.descripcion == "Pagado",
            Seguro.fecha_inicio <= fecha_actual,
            Seguro.fecha_fin >= fecha_actual
        ).first()

        estado_seguro = "Pagado" if seguro_pagado else "No Pagado"

        return jsonify({
            'pagos': pagos_data,
            'estado_seguro': estado_seguro
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@tractocamion_bp.route('/tractocamiones/<string:placa>/manifiestos', methods=['GET'])
def obtener_manifiestos(placa):
    try:
        # Obtener manifiestos asociados al tractocamión por placa
        manifiestos = Manifiesto.query.filter_by(placa=placa).all()
        manifiestos_data = [
            {
                'id': manifiesto.id,
                'numero': manifiesto.numero,
                'placa': manifiesto.placa,
                'conductor': manifiesto.conductor,
                'origen': manifiesto.origen,
                'destino': manifiesto.destino,
                'fecha': manifiesto.fecha.strftime('%Y-%m-%d'),
                'mes': manifiesto.mes,
                'kof1': manifiesto.kof1,
                'remesa': manifiesto.remesa,
                'empresa': manifiesto.empresa,
                'valor_flete': manifiesto.valor_flete
            }
            for manifiesto in manifiestos
        ]

        return jsonify({'manifiestos': manifiestos_data}), 200
    except Exception as e:
        print(f"Error al obtener manifiestos: {e}")
        return jsonify({'error': str(e)}), 500