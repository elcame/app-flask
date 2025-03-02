from flask import Blueprint, request, redirect, url_for
from extensions import db
from models.viajes import Viajes
viajes_bp = Blueprint('viajes_bp', __name__)

@viajes_bp.route('/viajes', methods=['GET'])
def get_viajes():
    viajes = Viajes.query.all()
    return jsonify([viaje.as_dict() for viaje in viajes])

@viajes_bp.route('/viajes', methods=['POST'])
def add_viaje():
    try:
        data = request.form
        new_viaje = Viajes(
            ORIGEN=data['origen'],
            DESTINO=data['destino'],
            FECHA_SALIDA=data['fecha_salida'],
            FECHA_LLEGADA=data['fecha_llegada'],
            ID_TRACTO=data['id_tracto']
        )
        db.session.add(new_viaje)
        db.session.commit()
        return redirect(url_for('tractocamion_bp.tractocamion_detail', id=data['id_tracto']))
    except Exception as e:
        return str(e), 500

@viajes_bp.route('/viajes/<int:id>', methods=['DELETE'])
def delete_viaje(id):
    viaje = Viajes.query.get(id)
    if viaje:
        db.session.delete(viaje)
        db.session.commit()
        return jsonify({'message': 'Viaje deleted!'}), 200
    else:
        return jsonify({'message': 'Viaje not found'}), 404

@viajes_bp.route('/viajes/<int:id>', methods=['PUT'])
def update_viaje(id):
    viaje = Viajes.query.get(id)
    if viaje:
        data = request.get_json()
        viaje.ORIGEN = data.get('origen', viaje.ORIGEN)
        viaje.DESTINO = data.get('destino', viaje.DESTINO)
        viaje.FECHA_SALIDA = data.get('fecha_salida', viaje.FECHA_SALIDA)
        viaje.FECHA_LLEGADA = data.get('fecha_llegada', viaje.FECHA_LLEGADA)
        viaje.ID_TRACTO = data.get('id_tracto', viaje.ID_TRACTO)
        db.session.commit()
        return jsonify({'message': 'Viaje updated!', 'ID_VIAJE': viaje.ID_VIAJE}), 200
    else:
        return jsonify({'message': 'Viaje not found'}), 404