"""
Generador de reportes PDF usando ReportLab con diseño corporativo de FresaTerra
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.lib import colors


class PDFReportGenerator:
    """Generador de reportes PDF con diseño corporativo"""
    
    def __init__(self):
        # Colores corporativos de FresaTerra
        self.colors = {
            'primary': HexColor('#DC2626'),      # Rojo FRESA
            'secondary': HexColor('#16A34A'),    # Verde TERRA
            'accent': HexColor('#1F2937'),       # Gris oscuro
            'light_gray': HexColor('#F3F4F6'),   # Gris claro
            'dark_gray': HexColor('#6B7280'),    # Gris medio
            'white': HexColor('#FFFFFF'),
            'success': HexColor('#10B981'),
            'warning': HexColor('#F59E0B'),
            'danger': HexColor('#EF4444')
        }
        
        # Configuración de página
        self.page_width, self.page_height = A4
        self.margin = 2*cm
        self.content_width = self.page_width - (2 * self.margin)
        
        # Estilos de texto
        self.styles = self._create_styles()
        
        # Ruta del logo
        self.logo_path = self._get_logo_path()
    
    def _create_styles(self):
        """Crea los estilos de texto personalizados"""
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=self.colors['secondary'],
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Texto de sección
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.colors['accent'],
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal personalizado
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.colors['accent'],
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Texto pequeño
        styles.add(ParagraphStyle(
            name='SmallText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=self.colors['dark_gray'],
            spaceAfter=4,
            fontName='Helvetica'
        ))
        
        return styles
    
    def _get_logo_path(self):
        """Obtiene la ruta del logo de la empresa"""
        # Buscar el logo en la estructura del proyecto
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'images', 'logo.png'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'images', 'logoBlanco.png'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'images', 'Fresa-removebg-preview.png')
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
        
        return None
    
    def generate_report(self, server_data: Dict[str, Any], output_path: str, report_config: Dict[str, Any]) -> bool:
        """Genera el reporte PDF completo"""
        try:
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Construir el contenido
            story = []
            
            # Encabezado corporativo
            story.extend(self._create_header(report_config))
            
            # Información del período
            story.extend(self._create_period_info(server_data))
            
            # Resumen ejecutivo
            story.extend(self._create_executive_summary(server_data))
            
            # Datos detallados
            story.extend(self._create_detailed_data(server_data))
            
            # Gráficos (si están disponibles)
            story.extend(self._create_charts_section(server_data))
            
            # Pie de página
            story.extend(self._create_footer())
            
            # Generar el PDF
            doc.build(story, onFirstPage=self._add_page_decorations, onLaterPages=self._add_page_decorations)
            
            print(f"✅ PDF generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generando PDF: {str(e)}")
            return False
    
    def _create_header(self, report_config: Dict[str, Any]) -> List:
        """Crea el encabezado del reporte"""
        story = []
        
        # Logo y título en la misma línea
        header_data = []
        if self.logo_path and os.path.exists(self.logo_path):
            # Crear tabla con logo y título
            logo_img = Image(self.logo_path, width=3*cm, height=1.5*cm)
            title_text = Paragraph("FRESA<font color='#16A34A'>TERRA</font>", self.styles['CustomTitle'])
            header_data = [[logo_img, title_text]]
        else:
            # Solo título si no hay logo
            title_text = Paragraph("FRESA<font color='#16A34A'>TERRA</font>", self.styles['CustomTitle'])
            header_data = [[title_text]]
        
        if header_data:
            header_table = Table(header_data, colWidths=[4*cm, self.content_width-4*cm])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            story.append(header_table)
        
        # Línea decorativa
        story.append(Spacer(1, 10))
        line_data = [['']]
        line_table = Table(line_data, colWidths=[self.content_width])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 3, self.colors['primary']),
        ]))
        story.append(line_table)
        
        # Título del reporte
        story.append(Spacer(1, 20))
        story.append(Paragraph(report_config['title'], self.styles['CustomSubtitle']))
        
        return story
    
    def _create_period_info(self, server_data: Dict[str, Any]) -> List:
        """Crea la información del período"""
        story = []
        
        try:
            data = server_data.get('data', {})
            periodo = data.get('periodo', {})
            
            if periodo:
                fecha_inicio = periodo.get('fecha_inicio', 'N/A')
                fecha_fin = periodo.get('fecha_fin', 'N/A')
                
                # Formatear fechas
                try:
                    if 'T' in fecha_inicio:
                        fecha_inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                    if 'T' in fecha_fin:
                        fecha_fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                except:
                    pass
                
                period_text = f"<b>Período de Análisis:</b> {fecha_inicio} - {fecha_fin}"
                story.append(Paragraph(period_text, self.styles['CustomNormal']))
                story.append(Spacer(1, 10))
        
        except Exception as e:
            print(f"⚠️ Error procesando información del período: {str(e)}")
        
        return story
    
    def _create_executive_summary(self, server_data: Dict[str, Any]) -> List:
        """Crea el resumen ejecutivo"""
        story = []
        
        try:
            story.append(Paragraph("Resumen Ejecutivo", self.styles['SectionHeader']))
            
            data = server_data.get('data', {})
            resumen = data.get('resumen_ejecutivo', {})
            
            if resumen:
                summary_data = []
                
                # Formatear datos del resumen
                if 'total_ventas' in resumen:
                    summary_data.append(['Total de Ventas:', f"S/. {resumen['total_ventas']}"])
                if 'total_pedidos' in resumen:
                    summary_data.append(['Total de Pedidos:', str(resumen['total_pedidos'])])
                if 'ticket_promedio' in resumen:
                    summary_data.append(['Ticket Promedio:', f"S/. {resumen['ticket_promedio']:.2f}"])
                if 'dias_analizados' in resumen:
                    summary_data.append(['Días Analizados:', str(resumen['dias_analizados'])])
                
                if summary_data:
                    summary_table = Table(summary_data, colWidths=[self.content_width*0.4, self.content_width*0.6])
                    summary_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), self.colors['light_gray']),
                        ('TEXTCOLOR', (0, 0), (0, -1), self.colors['accent']),
                        ('TEXTCOLOR', (1, 0), (1, -1), self.colors['secondary']),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                        ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
                    ]))
                    story.append(summary_table)
                    story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando resumen ejecutivo: {str(e)}")
        
        return story
    
    def _create_detailed_data(self, server_data: Dict[str, Any]) -> List:
        """Crea las secciones de datos detallados"""
        story = []
        
        try:
            data = server_data.get('data', {})
            datos_reporte = data.get('datos_reporte', {})
            
            if datos_reporte:
                # Resumen general
                story.extend(self._create_general_summary(datos_reporte))
                
                # Estados de pedidos
                story.extend(self._create_order_status_section(datos_reporte))
                
                # Top productos
                story.extend(self._create_top_products_section(datos_reporte))
                
                # Ventas por día
                story.extend(self._create_daily_sales_section(datos_reporte))
                
                # Estadísticas adicionales
                story.extend(self._create_additional_stats(datos_reporte))
        
        except Exception as e:
            print(f"⚠️ Error creando datos detallados: {str(e)}")
        
        return story
    
    def _create_general_summary(self, datos_reporte: Dict[str, Any]) -> List:
        """Crea el resumen general"""
        story = []
        
        try:
            resumen = datos_reporte.get('resumen', {})
            if not resumen:
                return story
            
            story.append(Paragraph("Métricas Generales", self.styles['SectionHeader']))
            
            metrics_data = []
            metrics = [
                ('Total de Pedidos', resumen.get('total_pedidos', 0)),
                ('Total de Ventas', f"S/. {resumen.get('total_ventas', '0.00')}"),
                ('Total de Envíos', resumen.get('total_envios', 0)),
                ('Ticket Promedio', f"S/. {resumen.get('ticket_promedio', 0):.2f}"),
                ('Carritos Abandonados', resumen.get('carritos_abandonados', 0)),
                ('Tasa de Conversión', f"{resumen.get('tasa_conversion', 0)}%"),
                ('Promedio Venta Diaria', f"S/. {resumen.get('promedio_venta_diaria', 0):.2f}")
            ]
            
            for metric, value in metrics:
                metrics_data.append([metric, str(value)])
            
            metrics_table = Table(metrics_data, colWidths=[self.content_width*0.6, self.content_width*0.4])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando resumen general: {str(e)}")
        
        return story
    
    def _create_order_status_section(self, datos_reporte: Dict[str, Any]) -> List:
        """Crea la sección de estados de pedidos"""
        story = []
        
        try:
            pedidos_por_estado = datos_reporte.get('pedidos_por_estado', {})
            if not pedidos_por_estado:
                return story
            
            story.append(Paragraph("Distribución por Estados de Pedidos", self.styles['SectionHeader']))
            
            status_data = [['Estado', 'Cantidad', 'Porcentaje']]
            total_pedidos = sum(pedidos_por_estado.values())
            
            for estado, cantidad in pedidos_por_estado.items():
                porcentaje = (cantidad / total_pedidos * 100) if total_pedidos > 0 else 0
                status_data.append([
                    estado.replace('_', ' ').title(),
                    str(cantidad),
                    f"{porcentaje:.1f}%"
                ])
            
            status_table = Table(status_data, colWidths=[self.content_width*0.5, self.content_width*0.25, self.content_width*0.25])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
            ]))
            story.append(status_table)
            story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando sección de estados: {str(e)}")
        
        return story
    
    def _create_top_products_section(self, datos_reporte: Dict[str, Any]) -> List:
        """Crea la sección de productos más vendidos"""
        story = []
        
        try:
            top_productos = datos_reporte.get('top_productos', [])
            if not top_productos:
                return story
            
            story.append(Paragraph("Productos Más Vendidos", self.styles['SectionHeader']))
            
            products_data = [['Producto', 'Cantidad Vendida', 'Ingresos Generados']]
            
            for i, producto in enumerate(top_productos[:5]):  # Top 5 productos
                products_data.append([
                    producto.get('nombre', 'N/A'),
                    str(producto.get('total_vendidos', '0')),
                    f"S/. {producto.get('ingresos_generados', '0.00')}"
                ])
            
            products_table = Table(products_data, colWidths=[self.content_width*0.5, self.content_width*0.25, self.content_width*0.25])
            products_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
            ]))
            story.append(products_table)
            story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando sección de productos: {str(e)}")
        
        return story
    
    def _create_daily_sales_section(self, datos_reporte: Dict[str, Any]) -> List:
        """Crea la sección de ventas por día"""
        story = []
        
        try:
            ventas_por_dia = datos_reporte.get('ventas_por_dia', [])
            if not ventas_por_dia:
                return story
            
            story.append(Paragraph("Ventas por Día", self.styles['SectionHeader']))
            
            sales_data = [['Fecha', 'Total Ventas', 'Transacciones']]
            
            for venta in ventas_por_dia[-10:]:  # Últimos 10 días
                fecha = venta.get('fecha', 'N/A')
                try:
                    # Formatear fecha
                    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                    fecha = fecha_obj.strftime('%d/%m/%Y')
                except:
                    pass
                
                sales_data.append([
                    fecha,
                    f"S/. {venta.get('total_ventas', '0.00')}",
                    str(venta.get('cantidad_transacciones', '0'))
                ])
            
            sales_table = Table(sales_data, colWidths=[self.content_width*0.4, self.content_width*0.3, self.content_width*0.3])
            sales_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
            ]))
            story.append(sales_table)
            story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando sección de ventas diarias: {str(e)}")
        
        return story
    
    def _create_additional_stats(self, datos_reporte: Dict[str, Any]) -> List:
        """Crea la sección de estadísticas adicionales"""
        story = []
        
        try:
            stats_adicionales = datos_reporte.get('estadisticas_adicionales', {})
            if not stats_adicionales:
                return story
            
            story.append(Paragraph("Estadísticas Adicionales", self.styles['SectionHeader']))
            
            additional_data = []
            stats = [
                ('Días con Ventas', stats_adicionales.get('dias_con_ventas', 0)),
                ('Mayor Venta Diaria', f"S/. {stats_adicionales.get('mayor_venta_diaria', '0.00')}"),
                ('Menor Venta Diaria', f"S/. {stats_adicionales.get('menor_venta_diaria', '0.00')}"),
                ('Promedio Transacciones/Día', f"{stats_adicionales.get('promedio_transacciones_dia', 0):.1f}")
            ]
            
            for stat, value in stats:
                additional_data.append([stat, str(value)])
            
            additional_table = Table(additional_data, colWidths=[self.content_width*0.6, self.content_width*0.4])
            additional_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['warning']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['dark_gray']),
            ]))
            story.append(additional_table)
            story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando estadísticas adicionales: {str(e)}")
        
        return story
    
    def _create_charts_section(self, server_data: Dict[str, Any]) -> List:
        """Crea la sección de gráficos (placeholder para futura implementación)"""
        story = []
        
        try:
            data = server_data.get('data', {})
            datos_especificos = data.get('datos_reporte', {}).get('datos_especificos', {})
            chart_data = datos_especificos.get('chart_data', {})
            
            if chart_data:
                story.append(Paragraph("Análisis Gráfico", self.styles['SectionHeader']))
                
                # Información sobre los gráficos disponibles
                chart_info = chart_data.get('description', 'Datos gráficos disponibles en el sistema')
                story.append(Paragraph(f"<i>{chart_info}</i>", self.styles['CustomNormal']))
                
                # Nota sobre visualización
                story.append(Paragraph(
                    "<b>Nota:</b> Para visualizar los gráficos detallados, consulte la interfaz principal de estadísticas.",
                    self.styles['SmallText']
                ))
                story.append(Spacer(1, 20))
        
        except Exception as e:
            print(f"⚠️ Error creando sección de gráficos: {str(e)}")
        
        return story
    
    def _create_footer(self) -> List:
        """Crea el pie de página del reporte"""
        story = []
        
        # Línea separadora
        line_data = [['']]
        line_table = Table(line_data, colWidths=[self.content_width])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 2, self.colors['primary']),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 10))
        
        # Información de generación
        timestamp = datetime.now().strftime("%d/%m/%Y a las %H:%M")
        footer_text = f"<i>Reporte generado automáticamente el {timestamp} por el Sistema de Administración FresaTerra</i>"
        story.append(Paragraph(footer_text, self.styles['SmallText']))
        
        return story
    
    def _add_page_decorations(self, canvas, doc):
        """Añade decoraciones a cada página"""
        # Marca de agua sutil
        canvas.saveState()
        canvas.setFillColor(self.colors['light_gray'])
        canvas.setFont("Helvetica", 50)
        canvas.rotate(45)
        canvas.drawCentredString(400, 0, "FresaTerra")
        canvas.restoreState()
        
        # Número de página
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(self.colors['dark_gray'])
        canvas.drawRightString(
            self.page_width - self.margin,
            self.margin - 15,
            f"Página {doc.page}"
        )
        canvas.restoreState()
