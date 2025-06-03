from flask import Blueprint, render_template, send_file, jsonify
from flask_login import login_required, current_user
import pandas as pd
import os
from datetime import datetime
import logging
from models.manifiesto import Manifiesto
from extensions import db

exportar_bp = Blueprint('exportar_bp', __name__)
logger = logging.getLogger(__name__)

@exportar_bp.route('/exportar')
@login_required
def exportar():
    try:
        return render_template('exportar/index.html')
    except Exception as e:
        logger.error(f"Error en página de exportar: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exportar_bp.route('/exportar/manifiestos')
@login_required
def exportar_manifiestos():
    try:
        # Crear directorio si no existe
        os.makedirs('excel/manifiestos', exist_ok=True)
        
        # Generar nombre de archivo con fecha
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'manifiestos_{fecha}.xlsx'
        filepath = os.path.join('excel/manifiestos', filename)
        
        # Obtener todos los manifiestos de la base de datos
        manifiestos = Manifiesto.query.all()
        
        # Crear DataFrame con los datos
        datos = []
        for manifiesto in manifiestos:
            datos.append({
                'ID': manifiesto.id,
                'Número': manifiesto.numero,
                'Placa': manifiesto.placa,
                'Conductor': manifiesto.conductor,
                'Origen': manifiesto.origen,
                'Destino': manifiesto.destino,
                'Fecha': manifiesto.fecha.strftime('%d/%m/%Y') if manifiesto.fecha else '',
                'Mes': manifiesto.mes,
                'KOF': manifiesto.kof1,
                'Remesa': manifiesto.remesa,
                'Empresa': manifiesto.empresa,
                'Valor Flete': f"${manifiesto.valor_flete:,.2f}" if manifiesto.valor_flete else '',
                'Ruta PDF': manifiesto.pdf_path
            })
        
        df = pd.DataFrame(datos)
        
        # Crear un writer de Excel con formato
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Manifiestos')
            
            # Obtener la hoja de trabajo
            worksheet = writer.sheets['Manifiestos']
            
            # Ajustar el ancho de las columnas
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Error al exportar manifiestos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exportar_bp.route('/exportar/reportes')
@login_required
def exportar_reportes():
    try:
        # Crear directorio si no existe
        os.makedirs('excel/reportes', exist_ok=True)
        
        # Generar nombre de archivo con fecha
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reportes_{fecha}.xlsx'
        filepath = os.path.join('excel/reportes', filename)
        
        # Obtener datos de manifiestos para el reporte
        manifiestos = Manifiesto.query.all()
        
        # Crear DataFrame con los datos del reporte
        datos = []
        for manifiesto in manifiestos:
            datos.append({
                'ID': manifiesto.id,
                'Placa': manifiesto.placa,
                'Conductor': manifiesto.conductor,
                'Ruta': f"{manifiesto.origen} - {manifiesto.destino}",
                'Fecha': manifiesto.fecha.strftime('%d/%m/%Y') if manifiesto.fecha else '',
                'Mes': manifiesto.mes,
                'KOF': manifiesto.kof1,
                'Valor Flete': f"${manifiesto.valor_flete:,.2f}" if manifiesto.valor_flete else '',
                'Empresa': manifiesto.empresa
            })
        
        df = pd.DataFrame(datos)
        
        # Crear un writer de Excel con formato
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Reportes')
            
            # Obtener la hoja de trabajo
            worksheet = writer.sheets['Reportes']
            
            # Ajustar el ancho de las columnas
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Error al exportar reportes: {str(e)}")
        return jsonify({'error': str(e)}), 500 