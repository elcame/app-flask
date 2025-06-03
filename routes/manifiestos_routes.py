from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.manifiesto import Manifiesto
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.trabajadores import Trabajadores
from extensions import db
import logging

manifiestos_bp = Blueprint('manifiestos_bp', __name__)
logger = logging.getLogger(__name__)

@manifiestos_bp.route('/manifiestos')
@login_required
def listar_manifiestos():
    try:
        # Obtener manifiestos de la empresa del usuario actual
        manifiestos = Manifiesto.query.filter_by(empresa_id=current_user.empresa_id).all()
        return render_template('manifiestos/lista.html', manifiestos=manifiestos)
    except Exception as e:
        logger.error(f"Error al listar manifiestos: {str(e)}")
        flash('Error al cargar los manifiestos', 'error')
        return redirect(url_for('usuario_bp.manifiestos'))

@manifiestos_bp.route('/manifiestos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_manifiesto():
    try:
        if request.method == 'POST':
            # Obtener datos del formulario
            tractocamion_id = request.form.get('tractocamion_id')
            trabajador_id = request.form.get('trabajador_id')
            fecha = request.form.get('fecha')
            
            # Crear nuevo manifiesto
            manifiesto = Manifiesto(
                empresa_id=current_user.empresa_id,
                tractocamion_id=tractocamion_id,
                trabajador_id=trabajador_id,
                fecha=fecha
            )
            
            db.session.add(manifiesto)
            db.session.commit()
            
            flash('Manifiesto creado exitosamente', 'success')
            return redirect(url_for('manifiestos_bp.listar_manifiestos'))
            
        # Obtener datos para el formulario
        tractocamiones = Tractocamion.query.filter_by(empresa_id=current_user.empresa_id).all()
        trabajadores = Trabajadores.query.filter_by(empresa_id=current_user.empresa_id).all()
        
        return render_template('manifiestos/nuevo.html', 
                             tractocamiones=tractocamiones,
                             trabajadores=trabajadores)
    except Exception as e:
        logger.error(f"Error al crear manifiesto: {str(e)}")
        flash('Error al crear el manifiesto', 'error')
        return redirect(url_for('manifiestos_bp.listar_manifiestos'))

@manifiestos_bp.route('/manifiestos/<int:id>')
@login_required
def ver_manifiesto(id):
    try:
        manifiesto = Manifiesto.query.get_or_404(id)
        if manifiesto.empresa_id != current_user.empresa_id:
            flash('No tienes permiso para ver este manifiesto', 'error')
            return redirect(url_for('manifiestos_bp.listar_manifiestos'))
            
        return render_template('manifiestos/ver.html', manifiesto=manifiesto)
    except Exception as e:
        logger.error(f"Error al ver manifiesto: {str(e)}")
        flash('Error al cargar el manifiesto', 'error')
        return redirect(url_for('manifiestos_bp.listar_manifiestos'))

@manifiestos_bp.route('/manifiestos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_manifiesto(id):
    try:
        manifiesto = Manifiesto.query.get_or_404(id)
        if manifiesto.empresa_id != current_user.empresa_id:
            flash('No tienes permiso para editar este manifiesto', 'error')
            return redirect(url_for('manifiestos_bp.listar_manifiestos'))
            
        if request.method == 'POST':
            # Actualizar datos del manifiesto
            manifiesto.tractocamion_id = request.form.get('tractocamion_id')
            manifiesto.trabajador_id = request.form.get('trabajador_id')
            manifiesto.fecha = request.form.get('fecha')
            
            db.session.commit()
            flash('Manifiesto actualizado exitosamente', 'success')
            return redirect(url_for('manifiestos_bp.listar_manifiestos'))
            
        # Obtener datos para el formulario
        tractocamiones = Tractocamion.query.filter_by(empresa_id=current_user.empresa_id).all()
        trabajadores = Trabajadores.query.filter_by(empresa_id=current_user.empresa_id).all()
        
        return render_template('manifiestos/editar.html',
                             manifiesto=manifiesto,
                             tractocamiones=tractocamiones,
                             trabajadores=trabajadores)
    except Exception as e:
        logger.error(f"Error al editar manifiesto: {str(e)}")
        flash('Error al editar el manifiesto', 'error')
        return redirect(url_for('manifiestos_bp.listar_manifiestos'))

@manifiestos_bp.route('/manifiestos/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_manifiesto(id):
    try:
        manifiesto = Manifiesto.query.get_or_404(id)
        if manifiesto.empresa_id != current_user.empresa_id:
            flash('No tienes permiso para eliminar este manifiesto', 'error')
            return redirect(url_for('manifiestos_bp.listar_manifiestos'))
            
        db.session.delete(manifiesto)
        db.session.commit()
        flash('Manifiesto eliminado exitosamente', 'success')
        return redirect(url_for('manifiestos_bp.listar_manifiestos'))
    except Exception as e:
        logger.error(f"Error al eliminar manifiesto: {str(e)}")
        flash('Error al eliminar el manifiesto', 'error')
        return redirect(url_for('manifiestos_bp.listar_manifiestos')) 