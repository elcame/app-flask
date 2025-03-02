from flask import Blueprint, request, redirect, url_for, render_template
from extensions import db
from models.tractocamion import Tractocamion


tractocamion_bp = Blueprint('tractocamion_bp', __name__)

@tractocamion_bp.route('/tractocamiones', methods=['GET'])
def get_tractocamiones():
    tractocamiones = Tractocamion.query.all()
    return jsonify([tractocamion.as_dict() for tractocamion in tractocamiones])

@tractocamion_bp.route('/tractocamiones', methods=['POST'])
def add_tractocamion():
    try:
        data = request.form
        new_tractocamion = Tractocamion(
            MARCA=data['marca'],
            MODELO=data['modelo'],
            PLACA=data['placa'],
            ID_EMPRESA=session['id_empresa']
        )
        db.session.add(new_tractocamion)
        db.session.commit()
        return redirect(url_for('usuario_bp.inicio'))
    except Exception as e:
        return str(e), 500

@tractocamion_bp.route('/tractocamiones/<int:id>', methods=['GET'])
def tractocamion_detail(id):
    tractocamion = Tractocamion.query.get(id)
    if tractocamion:
        return render_template('tractocamiones.html', tractocamion=tractocamion)
    else:
        return 'Tractocamion not found', 404