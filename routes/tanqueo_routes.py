from flask import Blueprint, request, jsonify, render_template
from extensions import db
from models.tanqueo import Tanqueo

tanqueo_bp = Blueprint('tanqueo_bp', __name__)

@tanqueo_bp.route('/tanqueos', methods=['GET'])
def get_tanqueos():
    tanqueos = Tanqueo.query.all()
    return jsonify([tanqueo.as_dict() for tanqueo in tanqueos])

@tanqueo_bp.route('/tanqueos/new', methods=['GET'])
def new_tanqueo_form():
    return render_template('tanqueo_form.html')

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

@tanqueo_bp.route('/tanqueos/<int:id>', methods=['DELETE'])
def delete_tanqueo(id):
    tanqueo = Tanqueo.query.get(id)
    if tanqueo:
        db.session.delete(tanqueo)
        db.session.commit()
        return jsonify({'message': 'Tanqueo deleted!'}), 200
    else:
        return jsonify({'message': 'Tanqueo not found'}), 404

@tanqueo_bp.route('/tanqueos/<int:id>', methods=['PUT'])
def update_tanqueo(id):
    tanqueo = Tanqueo.query.get(id)
    if tanqueo:
        data = request.get_json()
        tanqueo.CANTIDAD = data.get('cantidad', tanqueo.CANTIDAD)
        tanqueo.FECHA = data.get('fecha', tanqueo.FECHA)
        tanqueo.ID_TRACTO = data.get('id_tracto', tanqueo.ID_TRACTO)
        db.session.commit()
        return jsonify({'message': 'Tanqueo updated!', 'ID_TANQUEO': tanqueo.ID_TANQUEO}), 200
    else:
        return jsonify({'message': 'Tanqueo not found'}), 404