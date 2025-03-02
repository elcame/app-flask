from flask import Blueprint, request, redirect, url_for
from extensions import db
from models.tanqueo import Tanqueo

tanqueo_bp = Blueprint('tanqueo_bp', __name__)

@tanqueo_bp.route('/tanqueos', methods=['POST'])
def add_tanqueo():
    try:
        data = request.form
        new_tanqueo = Tanqueo(
            CANTIDAD=data['cantidad'],
            FECHA=data['fecha'],
            ID_TRACTO=data['id_tracto']
        )
        db.session.add(new_tanqueo)
        db.session.commit()
        return redirect(url_for('tractocamion_bp.tractocamion_detail', id=data['id_tracto']))
    except Exception as e:
        return str(e), 500

mantenimiento_bp = Blueprint('mantenimiento_bp', __name__)

@mantenimiento_bp.route('/mantenimientos', methods=['GET'])
def get_mantenimientos():
    mantenimientos = Mantenimiento.query.all()
    return jsonify([mantenimiento.as_dict() for mantenimiento in mantenimientos])

@mantenimiento_bp.route('/mantenimiento', methods=['POST'])
def add_mantenimiento():
    try:
        data = request.form
        new_mantenimiento = Mantenimiento(
            DESCRIPCION=data['descripcion'],
            FECHA=data['fecha'],
            ID_TRACTO=data['id_tracto']
        )
        db.session.add(new_mantenimiento)
        db.session.commit()
        return redirect(url_for('tractocamion_bp.tractocamion_detail', id=data['id_tracto']))
    except Exception as e:
        return str(e), 500

@mantenimiento_bp.route('/mantenimientos/<int:id>', methods=['DELETE'])
def delete_mantenimiento(id):
    mantenimiento = Mantenimiento.query.get(id)
    if mantenimiento:
        db.session.delete(mantenimiento)
        db.session.commit()
        return jsonify({'message': 'Mantenimiento deleted!'}), 200
    else:
        return jsonify({'message': 'Mantenimiento not found'}), 404

@mantenimiento_bp.route('/mantenimientos/<int:id>', methods=['PUT'])
def update_mantenimiento(id):
    mantenimiento = Mantenimiento.query.get(id)
    if mantenimiento:
        data = request.get_json()
        mantenimiento.DESCRIPCION = data.get('descripcion', mantenimiento.DESCRIPCION)
        mantenimiento.FECHA = data.get('fecha', mantenimiento.FECHA)
        mantenimiento.COSTO = data.get('costo', mantenimiento.COSTO)
        mantenimiento.ID_TRACTO = data.get('id_tracto', mantenimiento.ID_TRACTO)
        db.session.commit()
        return jsonify({'message': 'Mantenimiento updated!', 'ID_MANTENIMIENTO': mantenimiento.ID_MANTENIMIENTO}), 200
    else:
        return jsonify({'message': 'Mantenimiento not found'}), 404 