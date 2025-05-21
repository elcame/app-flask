from flask import Blueprint, request, jsonify, render_template
from extensions import db
from models.mantenimiento import Mantenimiento, MantenimientoRepuestos
from models.pago import Pago

mantenimiento_bp = Blueprint('mantenimiento_bp', __name__)

@mantenimiento_bp.route('/mantenimiento', methods=['POST'])
def registrar_mantenimiento():
    data = request.get_json()
    try:
        # Validar datos requeridos
        if not data.get('placa') or not data.get('fecha') or not data.get('valor_total'):
            return jsonify({'error': 'Placa, fecha y valor total son obligatorios'}), 400

        # Crear un nuevo mantenimiento
        nuevo_mantenimiento = Mantenimiento(
            placa=data['placa'],
            fecha=data['fecha'],
            valor_total=data['valor_total'],
            taller=data.get('taller'),
            km_actual=data.get('km_actual'),
            proximo_km=data.get('proximo_km'),
            observaciones=data.get('observaciones')
        )
        db.session.add(nuevo_mantenimiento)
        db.session.flush()  # Obtener el ID del mantenimiento antes de confirmar la transacción

        # Registrar los repuestos asociados
        valor_repuestos = 0
        for repuesto in data.get('repuestos', []):
            if not repuesto.get('repuesto') or not repuesto.get('valor'):
                return jsonify({'error': 'Cada repuesto debe tener un nombre y un valor'}), 400

            nuevo_repuesto = MantenimientoRepuestos(
                id_mantenimiento=nuevo_mantenimiento.id,
                repuesto=repuesto['repuesto'],
                valor=repuesto['valor']
            )
            valor_repuestos += repuesto['valor']
            db.session.add(nuevo_repuesto)

        # Crear un registro en la tabla de pagos para el mantenimiento
        nuevo_pago_mantenimiento = Pago(
            tipo_pago='mantenimiento',
            id_referencia=nuevo_mantenimiento.id,
            monto=data['valor_total'],
            fecha_pago=data['fecha'],
            placa=data['placa']
        )
        db.session.add(nuevo_pago_mantenimiento)

        # Crear un registro en la tabla de pagos para los repuestos
        if valor_repuestos > 0:
            nuevo_pago_repuestos = Pago(
                tipo_pago='repuestos',
                id_referencia=nuevo_mantenimiento.id,
                monto=valor_repuestos,
                fecha_pago=data['fecha'],
                placa=data['placa']
            )
            db.session.add(nuevo_pago_repuestos)

        # Confirmar los cambios en la base de datos
        db.session.commit()

        return jsonify({'message': 'Mantenimiento, repuestos y pagos registrados correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar mantenimiento: {e}")
        return jsonify({'error': str(e)}), 500


@mantenimiento_bp.route('/mantenimiento', methods=['GET'])
def ver_mantenimientos():
    mantenimientos = Mantenimiento.query.all()
    repuestos = MantenimientoRepuestos.query.all()
    return render_template('mantenimiento.html', mantenimientos=mantenimientos, repuestos=repuestos)

@mantenimiento_bp.route('/mantenimiento/<int:id_mantenimiento>/repuestos', methods=['GET'])
def obtener_repuestos(id_mantenimiento):
    try:
        repuestos = MantenimientoRepuestos.query.filter_by(id_mantenimiento=id_mantenimiento).all()
        mantenimiento = Mantenimiento.query.get(id_mantenimiento)

        if not mantenimiento:
            return jsonify({'error': 'Mantenimiento no encontrado'}), 404

        repuestos_data = [
            {
                'id': repuesto.id,
                'id_mantenimiento': repuesto.id_mantenimiento,
                'repuesto': repuesto.repuesto,
                'valor': repuesto.valor
            }
            for repuesto in repuestos
        ]

        # Calcular la suma total de los repuestos y el mantenimiento
        suma_repuestos = sum(repuesto.valor for repuesto in repuestos)
        suma_total = suma_repuestos + mantenimiento.valor_total

        return jsonify({
            'repuestos': repuestos_data,
            'suma_repuestos': suma_repuestos,
            'suma_total': suma_total
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mantenimiento_bp.route('/mantenimiento/<int:id_mantenimiento>', methods=['DELETE'])
def eliminar_mantenimiento(id_mantenimiento):
    try:
        # Eliminar los repuestos asociados
        MantenimientoRepuestos.query.filter_by(id_mantenimiento=id_mantenimiento).delete()

        # Eliminar el mantenimiento
        mantenimiento = Mantenimiento.query.get(id_mantenimiento)
        if not mantenimiento:
            return jsonify({'error': 'Mantenimiento no encontrado'}), 404

        db.session.delete(mantenimiento)
        db.session.commit()

        return jsonify({'message': f'Mantenimiento con ID {id_mantenimiento} y sus repuestos asociados han sido eliminados correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500