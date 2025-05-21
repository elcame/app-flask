from flask import Blueprint, request, jsonify, render_template
from extensions import db
from models.seguro import Seguro
from models.tractocamion import Tractocamion
from models.pago import Pago
seguro_bp = Blueprint('seguro_bp', __name__)

@seguro_bp.route('/seguros', methods=['GET'])
def ver_seguros():
    seguros = Seguro.query.all()
    return render_template('seguro.html', seguros=seguros)

@seguro_bp.route('/seguros', methods=['POST'])
def agregar_seguro():
    data = request.get_json()
    try:
        nuevo_seguro = Seguro(
            placa=data['placa'],
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            valor=data['valor'],
            descripcion=data.get('descripcion')
        )
        db.session.add(nuevo_seguro)
        db.session.commit()
        return jsonify({'message': 'Seguro agregado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al agregar seguro: {e}")
        return jsonify({'error': str(e)}), 500
@seguro_bp.route('/seguros/<int:id>/pagar', methods=['POST'])
def pagar_seguro(id):
    try:
        seguro = Seguro.query.get(id)
        if not seguro:
            return jsonify({'error': 'Seguro no encontrado'}), 404

        if seguro.descripcion == "Pagado":
            return jsonify({'error': 'El seguro ya está pagado'}), 400

        # Marcar el seguro como pagado
        seguro.descripcion = "Pagado"

        # Registrar el pago en la tabla 'pagos' (opcional)
        nuevo_pago = Pago(
                 tipo_pago="seguro",
            id_referencia=seguro.id,  # Asegúrate de usar el ID del seguro
            monto=seguro.valor,
            fecha_pago=db.func.current_date(),
            descripcion="Pago del seguro",
            placa=seguro.placa
            
        )
        db.session.add(nuevo_pago)
        db.session.commit()

        return jsonify({'message': 'Seguro pagado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al pagar seguro: {e}")
        return jsonify({'error': str(e)}), 500