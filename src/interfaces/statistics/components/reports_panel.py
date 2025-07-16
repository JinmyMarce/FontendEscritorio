"""
Panel de generación de reportes mejorado con integración a API y ReportLab
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from typing import Dict, Any, Optional
import requests
import json
from datetime import datetime
import os
import threading
import traceback
from ..statistics_service import StatisticsService

# Importación condicional del generador PDF
try:
    from .pdf_report_generator import PDFReportGenerator
except ImportError:
    print("PDFReportGenerator no disponible, creando versión básica")
    
    class PDFReportGenerator:
        def generate_report(self, server_data, output_path, report_config):
            # Versión básica sin ReportLab
            try:
                with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(f"REPORTE: {report_config['title']}\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"Datos del servidor:\n{json.dumps(server_data, indent=2, ensure_ascii=False)}")
                return True
            except:
                return False


class ReportsPanel(ctk.CTkFrame):
    """Panel para generación de reportes con tres botones verticales"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="#FFFFFF", 
            corner_radius=15,
            **kwargs
        )
        
        # Servicios
        self.statistics_service = StatisticsService()
        self.pdf_generator = PDFReportGenerator()
        
        # Estado
        self.current_period = None
        self.is_loading = False
        self.current_period_days = 7  # Por defecto 7 días
        
        self.setup_ui()
    
    
    def setup_ui(self):
        """Configura el panel de reportes con tres botones verticales"""
        # Header del panel
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        # Título del panel
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Generar Reportes",
            font=("Arial", 20, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        self.title_label.pack(side="left")
        
        # Estado dinámico
        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Listo para generar",
            font=("Arial", 11),
            text_color="#16A34A"
        )
        self.status_label.pack(side="right")
        
        # Contenido principal
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=12
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Crear los tres botones de reportes
        self.create_report_buttons()
    
    def create_report_buttons(self):
        """Crea los tres botones de reportes ordenados verticalmente"""
        # Frame principal para los botones
        buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        buttons_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Información del panel
        info_label = ctk.CTkLabel(
            buttons_frame,
            text="Selecciona el período y tipo de reporte que deseas generar en PDF",
            font=("Arial", 14),
            text_color="#6B7280",
            anchor="center"
        )
        info_label.pack(pady=(0, 20))
        
        # Crear selector de período de fechas
        self.create_date_selector(buttons_frame)
        
        # Separador visual
        separator = ctk.CTkFrame(buttons_frame, height=2, fg_color="#E5E7EB")
        separator.pack(fill="x", pady=(20, 30))
        
        # Configuración de los tres tipos de reportes
        report_types = [
            {
                "title": "📊 Ventas Diarias",
                "description": "Reporte detallado de ventas por día con gráficos y análisis de tendencias",
                "tipo_api": "ventas_diarias",
                "icon": "📈",
                "color": "#16A34A",
                "hover_color": "#15803D"
            },
            {
                "title": "📅 Ventas Mensuales", 
                "description": "Análisis mensual de ventas con comparativas y métricas de rendimiento",
                "tipo_api": "ventas_mensuales",
                "icon": "📊",
                "color": "#2563EB",
                "hover_color": "#1D4ED8"
            },
            {
                "title": "⚙️ Ventas Personalizadas",
                "description": "Reporte personalizado con filtros específicos y análisis avanzado",
                "tipo_api": "ventas_personalizadas",
                "icon": "🎯",
                "color": "#7C3AED",
                "hover_color": "#6D28D9"
            }
        ]
        
        # Crear cada botón de reporte
        for i, report in enumerate(report_types):
            self.create_report_button(buttons_frame, report, i)
    

    
    def create_report_button(self, parent, report_config, index):
        """Crea un botón individual de reporte"""
        # Frame contenedor del botón
        button_container = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=2,
            border_color="#E5E7EB",
            height=100
        )
        button_container.pack(fill="x", pady=(0, 15), padx=10)
        
        # Frame interno para el contenido
        content_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Frame izquierdo - Icono y título
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        # Icono grande
        icon_label = ctk.CTkLabel(
            left_frame,
            text=report_config["icon"],
            font=("Arial", 28)
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Información del reporte
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Título
        title_label = ctk.CTkLabel(
            info_frame,
            text=report_config["title"],
            font=("Arial", 16, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Descripción
        desc_label = ctk.CTkLabel(
            info_frame,
            text=report_config["description"],
            font=("Arial", 11),
            text_color="#6B7280",
            anchor="w",
            wraplength=300
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        
        # Botón de acción (lado derecho)
        action_button = ctk.CTkButton(
            content_frame,
            text="Generar PDF",
            command=lambda: self.generate_report(report_config),
            width=120,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color=report_config["color"],
            hover_color=report_config["hover_color"],
            corner_radius=8
        )
        action_button.pack(side="right", padx=(15, 0))
        
        # Efectos hover para el contenedor
        def on_enter(event):
            button_container.configure(border_color=report_config["color"])
        
        def on_leave(event):
            button_container.configure(border_color="#E5E7EB")
        
        button_container.bind("<Enter>", on_enter)
        button_container.bind("<Leave>", on_leave)
        
        # Hacer que todo el contenedor sea clickeable
        def on_click(event):
            if not self.is_loading:
                self.generate_report(report_config)
        
        button_container.bind("<Button-1>", on_click)
        content_frame.bind("<Button-1>", on_click)
        left_frame.bind("<Button-1>", on_click)
        info_frame.bind("<Button-1>", on_click)
    
    def set_current_period(self, fecha_inicio: str, fecha_fin: str):
        """Establece el período actual para los reportes"""
        try:
            from datetime import datetime, date
            
            # Validar formato de fechas
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            fecha_actual = date.today()
            
            print(f"📅 Validando período para reportes:")
            print(f"   Fecha inicio: {fecha_inicio} ({fecha_inicio_obj})")
            print(f"   Fecha fin: {fecha_fin} ({fecha_fin_obj})")
            print(f"   Fecha actual: {fecha_actual}")
            
            # Validar que fecha fin no sea futura
            if fecha_fin_obj > fecha_actual:
                print(f"⚠️ Advertencia: La fecha fin ({fecha_fin}) es posterior a la fecha actual ({fecha_actual})")
                print(f"🔧 Ajustando fecha fin a la fecha actual")
                fecha_fin = fecha_actual.strftime("%Y-%m-%d")
                fecha_fin_obj = fecha_actual
            
            # Validar que fecha inicio no sea posterior a fecha fin
            if fecha_inicio_obj > fecha_fin_obj:
                print(f"❌ Error: La fecha inicio ({fecha_inicio}) es posterior a la fecha fin ({fecha_fin})")
                return False
            
            self.current_period = (fecha_inicio, fecha_fin)
            print(f"✅ Período establecido para reportes: {fecha_inicio} a {fecha_fin}")
            return True
            
        except ValueError as e:
            print(f"❌ Error en formato de fechas: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error validando período: {str(e)}")
            return False
    
    def generate_report(self, report_config: Dict[str, Any]):
        """Genera un reporte específico usando las fechas del selector"""
        if self.is_loading:
            messagebox.showwarning("Generando", "Ya se está generando un reporte. Por favor espera.")
            return
        
        # Verificar que se hayan aplicado fechas válidas
        if not self.current_period:
            messagebox.showerror(
                "Error", 
                "No se ha establecido un período válido para el reporte.\n\n"
                "Por favor, seleccione las fechas y presione 'Aplicar'."
            )
            return
        
        # Validar fechas
        fecha_inicio, fecha_fin = self.current_period
        
        try:
            from datetime import datetime
            # Convertir fechas a objetos datetime para validación
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            fecha_actual = datetime.now()
            
            print(f"📅 Validando fechas para generar reporte:")
            print(f"   Fecha inicio: {fecha_inicio}")
            print(f"   Fecha fin: {fecha_fin}")
            print(f"   Fecha actual: {fecha_actual.strftime('%Y-%m-%d')}")
            
            # Verificar que la fecha fin no sea futura (más de 1 día)
            dias_diferencia = (fecha_fin_dt - fecha_actual).days
            
            if dias_diferencia > 1:
                messagebox.showerror(
                    "Error de Fecha", 
                    f"❌ La fecha fin ({fecha_fin}) no puede ser futura.\n\n"
                    f"Para generar reportes, la fecha fin debe ser la fecha actual o anterior.\n"
                    f"📅 Fecha actual: {fecha_actual.strftime('%Y-%m-%d')}\n\n"
                    f"Por favor, ajusta el período en el selector de fechas."
                )
                return
            
            # Si la fecha fin es muy antigua, advertir al usuario
            dias_antiguedad = (fecha_actual - fecha_fin_dt).days
            if dias_antiguedad > 7:
                result = messagebox.askyesno(
                    "Fecha de reporte antigua",
                    f"⚠️ La fecha fin del reporte ({fecha_fin}) es de hace {dias_antiguedad} días.\n\n"
                    f"📅 Fecha actual: {fecha_actual.strftime('%Y-%m-%d')}\n\n"
                    f"Para obtener datos más actuales, se recomienda ajustar el período.\n\n"
                    f"¿Deseas continuar con la fecha seleccionada?",
                    icon="warning"
                )
                if not result:
                    return
            
            print(f"✅ Validación de fechas exitosa")
            
        except Exception as e:
            print(f"⚠️ Error validando fechas: {str(e)}")
            # Continuar aunque haya error en validación
        
        # Ejecutar generación en hilo separado
        threading.Thread(
            target=self._generate_report_thread,
            args=(report_config,),
            daemon=True
        ).start()
    
    def _generate_report_thread(self, report_config: Dict[str, Any]):
        """Genera el reporte en un hilo separado"""
        try:
            self._set_loading_state(True, f"Generando {report_config['title']}")
            
            fecha_inicio, fecha_fin = self.current_period
            
            # 1. Solicitar datos al servidor
            response_data = self._fetch_report_data(
                report_config["tipo_api"], 
                fecha_inicio, 
                fecha_fin
            )
            
            if not response_data:
                raise Exception("No se pudieron obtener los datos del servidor")
            
            # 2. Generar PDF con ReportLab
            pdf_path = self._generate_pdf_report(response_data, report_config)
            
            if pdf_path:
                # 3. Verificar si usamos datos de fallback
                # Los datos de fallback SOLO tienen id_reporte = 999
                is_fallback = False
                report_id = None
                
                # Verificar diferentes estructuras de datos
                if 'data' in response_data and isinstance(response_data['data'], dict):
                    # Verificar estructura: response_data.data.data.id_reporte (datos anidados del servidor)
                    if 'data' in response_data['data']:
                        inner_data = response_data['data']['data']
                        report_id = inner_data.get('id_reporte')
                        print(f"🔍 Encontrado ID en estructura anidada: {report_id}")
                    else:
                        # Verificar estructura: response_data.data.id_reporte (datos directos)
                        report_id = response_data['data'].get('id_reporte')
                        print(f"🔍 Encontrado ID en estructura directa: {report_id}")
                else:
                    # Verificar estructura: response_data.id_reporte (datos en raíz)
                    report_id = response_data.get('id_reporte')
                    print(f"🔍 Encontrado ID en raíz: {report_id}")
                
                is_fallback = (report_id == 999)
                
                print(f"📊 Resultado final: {'Datos de demostración (fallback)' if is_fallback else 'Datos reales del servidor'}")
                print(f"   ID del reporte: {report_id}")
                
                if is_fallback:
                    # Mostrar advertencia sobre datos de demostración
                    self._show_fallback_success_message(pdf_path, report_config["title"])
                else:
                    # Mostrar éxito normal
                    self._show_success_message(pdf_path, report_config["title"])
            else:
                raise Exception("Error al generar el archivo PDF")
                
        except Exception as e:
            error_msg = f"Error al generar el reporte: {str(e)}"
            print(f"❌ {error_msg}")
            self._show_error_message(error_msg)
        finally:
            self._set_loading_state(False)
    
    def _fetch_report_data(self, tipo: str, fecha_inicio: str, fecha_fin: str) -> Optional[Dict[str, Any]]:
        """Solicita los datos del reporte al servidor"""
        try:
            from src.core.config import API_BASE_URL
            from src.shared.utils import APIHandler, SessionManager
            
            url = f"{API_BASE_URL}/admin/reports"
            
            payload = {
                "tipo": tipo,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "generar_inmediato": True,
                "descripcion_personalizada": f"Reporte {tipo} generado desde interfaz de administración"
            }
            
            # Validar y ajustar fecha fin si es futura
            try:
                from datetime import datetime, date
                fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                fecha_actual = date.today()
                
                if fecha_fin_obj > fecha_actual:
                    fecha_fin_ajustada = fecha_actual.strftime("%Y-%m-%d")
                    payload["fecha_fin"] = fecha_fin_ajustada
                    print(f"⚠️ Fecha fin ajustada de {fecha_fin} a {fecha_fin_ajustada} (fecha actual)")
                    
            except Exception as date_error:
                print(f"⚠️ Error validando fecha: {str(date_error)}")
            
            print(f"🔄 Solicitando datos al servidor: {url}")
            print(f"📤 Payload: {json.dumps(payload, indent=2)}")
            
            # Verificar que tenemos token de autenticación
            try:
                token = SessionManager.get_token()
                print(f"🔑 Token de autenticación: {'✅ Disponible' if token else '❌ No encontrado'}")
            except Exception as token_error:
                print(f"⚠️ Error obteniendo token: {str(token_error)}")
            
            # Usar APIHandler para manejar autenticación
            response = APIHandler.post(url, payload)
            
            print(f"📥 Respuesta del servidor:")
            print(f"   Status Code: {response.get('status_code', 'N/A')}")
            print(f"   Error: {response.get('error', 'N/A')}")
            
            # Manejo mejorado de la respuesta
            if response and response.get('status_code') == 200:
                # La respuesta viene anidada en 'data'
                response_data = response.get('data', {})
                print(f"   Response Data: {json.dumps(response_data, indent=2)}")
                
                # Verificar si tenemos los datos completos
                if 'data' in response_data and response_data.get('data'):
                    print(f"✅ Datos del reporte recibidos exitosamente")
                    print(f"   ID Reporte: {response_data['data'].get('id_reporte', 'N/A')}")
                    print(f"   Tipo: {response_data['data'].get('tipo', 'N/A')}")
                    print(f"   Estado: {response_data['data'].get('estado', 'N/A')}")
                    return response_data
                else:
                    print(f"⚠️ Respuesta exitosa pero sin datos de reporte")
                    return self._get_fallback_data()
            elif response and response.get('status_code') == 404:
                print(f"❌ Endpoint no encontrado (404). El servidor podría no tener implementado este endpoint.")
                # Usar datos de fallback si el endpoint no existe
                return self._get_fallback_data()
            elif response and response.get('status_code') == 401:
                print(f"❌ Error de autenticación (401). Token inválido o expirado.")
                return None
            elif response and response.get('status_code') == 400:
                # Manejo específico del error 400 (Bad Request)
                response_data = response.get('data', {})
                errores = response_data.get('errores', {})
                
                if 'fecha_fin' in errores:
                    print(f"❌ Error de fecha fin: {errores['fecha_fin']}")
                    print(f"💡 Sugerencia: La fecha fin debe ser igual o anterior a la fecha actual")
                else:
                    print(f"❌ Error de solicitud (400): {response_data.get('mensaje', 'Solicitud incorrecta')}")
                
                # Usar datos de fallback para error 400
                return self._get_fallback_data()
            elif response and response.get('status_code') == 409:
                # Manejo específico del error 409 (Conflict - reporte duplicado)
                response_data = response.get('data', {})
                print(f"⚠️ Reporte duplicado (409): {response_data.get('mensaje', 'Ya existe un reporte similar')}")
                
                reporte_existente = response_data.get('reporte_existente', {})
                if reporte_existente:
                    print(f"   ID del reporte existente: {reporte_existente.get('id_reporte', 'N/A')}")
                    print(f"   Estado: {reporte_existente.get('estado', 'N/A')}")
                    print(f"   Fecha: {reporte_existente.get('fecha_creacion', 'N/A')}")
                
                # Para reportes duplicados, usar datos de fallback con mensaje específico
                fallback_data = self._get_fallback_data()
                # Agregar información sobre el conflicto
                if fallback_data and 'data' in fallback_data:
                    fallback_data['conflicto_detectado'] = True
                    fallback_data['mensaje_conflicto'] = response_data.get('mensaje', 'Reporte duplicado')
                
                return fallback_data
            else:
                error_msg = response.get('error', 'Error desconocido') if response else 'No se pudo conectar al servidor'
                print(f"❌ Error del servidor: {error_msg}")
                # Usar datos de fallback en caso de error
                return self._get_fallback_data()
                
        except Exception as e:
            print(f"❌ Error en petición: {str(e)}")
            import traceback
            traceback.print_exc()
            # Usar datos de fallback en caso de excepción
            return self._get_fallback_data()
    
    def _generate_pdf_report(self, server_data: Dict[str, Any], report_config: Dict[str, Any]) -> Optional[str]:
        """Genera el PDF usando ReportLab"""
        try:
            print(f"🔄 Iniciando generación de PDF...")
            print(f"📊 Tipo de reporte: {report_config.get('tipo_api', 'N/A')}")
            print(f"📁 Datos recibidos: {json.dumps(server_data, indent=2)}")
            
            # Crear directorio de reportes si no existe
            reports_dir = os.path.join(os.path.expanduser("~"), "Documentos", "FresaTerra_Reportes")
            os.makedirs(reports_dir, exist_ok=True)
            print(f"📂 Directorio de reportes: {reports_dir}")
            
            # Nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_{report_config['tipo_api']}_{timestamp}.pdf"
            pdf_path = os.path.join(reports_dir, filename)
            print(f"📄 Archivo PDF: {pdf_path}")
            
            # Generar PDF usando ReportLab
            print(f"⚙️ Llamando al generador PDF...")
            success = self.pdf_generator.generate_report(
                server_data, 
                pdf_path, 
                report_config
            )
            
            print(f"📋 Resultado de generación: {'✅ Exitoso' if success else '❌ Falló'}")
            
            if success and os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"📏 Tamaño del archivo generado: {file_size} bytes")
                return pdf_path
            else:
                print(f"❌ El archivo PDF no se generó correctamente")
                return None
            
        except Exception as e:
            print(f"❌ Error generando PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _set_loading_state(self, loading: bool, message: str = ""):
        """Establece el estado de carga"""
        self.is_loading = loading
        
        if loading:
            self.status_label.configure(
                text=f"⏳ {message}...",
                text_color="#F59E0B"
            )
        else:
            self.status_label.configure(
                text="Listo para generar",
                text_color="#16A34A"
            )
    
    def _show_success_message(self, pdf_path: str, report_title: str):
        """Muestra mensaje de éxito y pregunta si abrir el PDF"""
        def show_dialog():
            result = messagebox.askyesno(
                "Reporte Generado",
                f"✅ {report_title} generado exitosamente\n\n"
                f"📁 Ubicación: {pdf_path}\n\n"
                "¿Deseas abrir el archivo PDF?",
                icon="question"
            )
            
            if result:
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(pdf_path)
                    else:  # Linux/Mac
                        os.system(f'xdg-open "{pdf_path}"')
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
        
        # Ejecutar en hilo principal
        self.after(0, show_dialog)
    
    def _show_error_message(self, error_msg: str):
        """Muestra mensaje de error"""
        def show_dialog():
            messagebox.showerror("Error", error_msg)
        
        # Ejecutar en hilo principal
        self.after(0, show_dialog)
    
    def _show_fallback_success_message(self, pdf_path: str, report_title: str):
        """Muestra mensaje de éxito cuando se usan datos de fallback"""
        def show_dialog():
            result = messagebox.askyesno(
                "Reporte Generado (Datos de Demostración)",
                f"⚠️ {report_title} generado con datos de demostración\n\n"
                f"📁 Ubicación: {pdf_path}\n\n"
                f"ℹ️ El servidor no respondió correctamente, por lo que se usaron\n"
                f"datos de ejemplo para generar el reporte.\n\n"
                "¿Deseas abrir el archivo PDF?",
                icon="warning"
            )
            
            if result:
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(pdf_path)
                    else:  # Linux/Mac
                        os.system(f'xdg-open "{pdf_path}"')
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
        
        # Ejecutar en hilo principal
        self.after(0, show_dialog)
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Retorna datos de fallback cuando no se puede conectar al servidor"""
        print("🔄 Usando datos de fallback para el reporte...")
        
        fecha_inicio, fecha_fin = self.current_period if self.current_period else ("2025-06-01", "2025-07-15")
        
        return {
            "mensaje": "Reporte generado con datos de demostración",
            "data": {
                "id_reporte": 999,
                "tipo": "demo",
                "estado": "generado",
                "periodo": {
                    "fecha_inicio": f"{fecha_inicio}T05:00:00.000000Z",
                    "fecha_fin": f"{fecha_fin}T05:00:00.000000Z"
                },
                "resumen_ejecutivo": {
                    "total_ventas": "1,250.75",
                    "total_pedidos": 34,
                    "ticket_promedio": 36.79,
                    "dias_analizados": 45
                },
                "datos_reporte": {
                    "periodo": {
                        "fecha_inicio": f"{fecha_inicio}T05:00:00.000000Z",
                        "fecha_fin": f"{fecha_fin}T05:00:00.000000Z"
                    },
                    "resumen": {
                        "total_pedidos": 34,
                        "total_ventas": "1,250.75",
                        "total_envios": 28,
                        "ticket_promedio": 36.79,
                        "carritos_abandonados": 3,
                        "tasa_conversion": 92,
                        "promedio_venta_diaria": 27.79
                    },
                    "pedidos_por_estado": {
                        "confirmado": 5,
                        "preparando": 8,
                        "en_camino": 12,
                        "entregado": 15,
                        "cancelado": 2
                    },
                    "top_productos": [
                        {
                            "nombre": "Frescura Familiar - 5kg",
                            "total_vendidos": "25",
                            "ingresos_generados": "1,300.00"
                        },
                        {
                            "nombre": "Delicia Andina - 1kg",
                            "total_vendidos": "18",
                            "ingresos_generados": "234.00"
                        },
                        {
                            "nombre": "Doble Dulzura - 2kg",
                            "total_vendidos": "12",
                            "ingresos_generados": "276.00"
                        }
                    ],
                    "ventas_por_dia": [
                        {"fecha": "2025-07-10", "total_ventas": "145.50", "cantidad_transacciones": 4},
                        {"fecha": "2025-07-11", "total_ventas": "89.25", "cantidad_transacciones": 2},
                        {"fecha": "2025-07-12", "total_ventas": "234.00", "cantidad_transacciones": 6},
                        {"fecha": "2025-07-13", "total_ventas": "178.75", "cantidad_transacciones": 5},
                        {"fecha": "2025-07-14", "total_ventas": "312.00", "cantidad_transacciones": 8},
                        {"fecha": "2025-07-15", "total_ventas": "203.25", "cantidad_transacciones": 7}
                    ],
                    "estadisticas_adicionales": {
                        "dias_con_ventas": 42,
                        "mayor_venta_diaria": "312.00",
                        "menor_venta_diaria": "15.50",
                        "promedio_transacciones_dia": 3.2
                    }
                }
            }
        }
    
    def create_date_selector(self, parent):
        """Crea el selector de fechas para el período del reporte"""
        # Frame contenedor del selector de fechas
        date_selector_frame = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=2,
            border_color="#E5E7EB"
        )
        date_selector_frame.pack(fill="x", pady=(0, 10))
        
        # Header del selector
        header_frame = ctk.CTkFrame(date_selector_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Título del selector
        title_label = ctk.CTkLabel(
            header_frame,
            text="📅 Período del Reporte",
            font=("Arial", 16, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        title_label.pack(side="left")
        
        # Botón de aplicar cambios
        self.apply_dates_button = ctk.CTkButton(
            header_frame,
            text="✓ Aplicar",
            command=self.apply_selected_dates,
            width=80,
            height=30,
            font=("Arial", 11, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D"
        )
        self.apply_dates_button.pack(side="right")
        
        # Frame para los controles de fecha
        controls_frame = ctk.CTkFrame(date_selector_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Configurar columnas
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=0)
        controls_frame.grid_columnconfigure(2, weight=1)
        
        # Frame para fecha inicio
        start_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        start_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        start_label = ctk.CTkLabel(
            start_frame,
            text="Fecha Inicio:",
            font=("Arial", 12, "bold"),
            text_color="#374151"
        )
        start_label.pack(anchor="w")
        
        # Entry para fecha inicio
        self.start_date_entry = ctk.CTkEntry(
            start_frame,
            placeholder_text="YYYY-MM-DD",
            width=120,
            height=35,
            font=("Arial", 12)
        )
        self.start_date_entry.pack(anchor="w", pady=(5, 0))
        
        # Agregar evento para actualizar fecha fin cuando cambie fecha inicio
        self.start_date_entry.bind("<KeyRelease>", self._on_start_date_change)
        self.start_date_entry.bind("<FocusOut>", self._on_start_date_change)
        
        # Separador visual
        separator_label = ctk.CTkLabel(
            controls_frame,
            text="—",
            font=("Arial", 20, "bold"),
            text_color="#6B7280"
        )
        separator_label.grid(row=0, column=1, padx=10)
        
        # Frame para fecha fin
        end_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        end_frame.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        
        end_label = ctk.CTkLabel(
            end_frame,
            text="Fecha Fin:",
            font=("Arial", 12, "bold"),
            text_color="#374151"
        )
        end_label.pack(anchor="w")
        
        # Entry para fecha fin (bloqueado)
        self.end_date_entry = ctk.CTkEntry(
            end_frame,
            placeholder_text="YYYY-MM-DD",
            width=120,
            height=35,
            font=("Arial", 12),
            state="disabled"
        )
        self.end_date_entry.pack(anchor="w", pady=(5, 0))
        
        # Frame para botones de fecha rápida
        quick_dates_frame = ctk.CTkFrame(date_selector_frame, fg_color="transparent")
        quick_dates_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Label para fechas rápidas
        quick_label = ctk.CTkLabel(
            quick_dates_frame,
            text="Seleccionar período:",
            font=("Arial", 11),
            text_color="#6B7280"
        )
        quick_label.pack(anchor="w", pady=(0, 5))
        
        # Frame para los botones
        buttons_frame = ctk.CTkFrame(quick_dates_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Botones de fecha rápida
        quick_date_configs = [
            {"text": "Hoy", "days": 0, "description": "Solo hoy"},
            {"text": "7 días", "days": 7, "description": "Última semana"},
            {"text": "30 días", "days": 30, "description": "Último mes"},
            {"text": "90 días", "days": 90, "description": "Últimos 3 meses"}
        ]
        
        for config in quick_date_configs:
            button = ctk.CTkButton(
                buttons_frame,
                text=config["text"],
                command=lambda d=config["days"], desc=config["description"]: self.set_period_days(d, desc),
                width=100,
                height=30,
                font=("Arial", 10),
                fg_color="#F3F4F6",
                text_color="#374151",
                hover_color="#E5E7EB",
                border_width=1,
                border_color="#D1D5DB"
            )
            button.pack(side="left", padx=(0, 8))
        
        # Label de estado del período
        self.period_status_label = ctk.CTkLabel(
            date_selector_frame,
            text="",
            font=("Arial", 10),
            text_color="#6B7280"
        )
        self.period_status_label.pack(pady=(0, 15))
        
        # Inicializar con fechas por defecto (última semana)
        self.current_period_days = 7  # Por defecto 7 días
        self.set_period_days(7, "Última semana")
    
    def set_period_days(self, days_back: int, description: str = ""):
        """Establece un período de días específico desde hoy hacia atrás"""
        from datetime import datetime, timedelta, date
        
        self.current_period_days = days_back
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=days_back)
        
        # Actualizar los campos de entrada
        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, fecha_inicio.strftime("%Y-%m-%d"))
        
        # Actualizar fecha fin (habilitando temporalmente para escribir)
        self.end_date_entry.configure(state="normal")
        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, fecha_fin.strftime("%Y-%m-%d"))
        self.end_date_entry.configure(state="disabled")
        
        # Aplicar automáticamente
        self.apply_selected_dates()
    
    def _on_start_date_change(self, event=None):
        """Actualiza la fecha fin cuando cambia la fecha inicio"""
        try:
            fecha_inicio_str = self.start_date_entry.get().strip()
            if len(fecha_inicio_str) == 10:  # YYYY-MM-DD formato completo
                from datetime import datetime, timedelta, date
                
                # Validar formato
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
                fecha_fin = fecha_inicio + timedelta(days=self.current_period_days)
                fecha_actual = date.today()
                
                # No permitir fecha fin futura
                if fecha_fin > fecha_actual:
                    fecha_fin = fecha_actual
                
                # Actualizar fecha fin
                self.end_date_entry.configure(state="normal")
                self.end_date_entry.delete(0, "end")
                self.end_date_entry.insert(0, fecha_fin.strftime("%Y-%m-%d"))
                self.end_date_entry.configure(state="disabled")
                
                # Aplicar cambios si el formato es válido
                self.apply_selected_dates()
                
        except (ValueError, AttributeError):
            # Fecha inválida o incompleta, no hacer nada
            pass
    
    def apply_selected_dates(self):
        """Aplica las fechas seleccionadas al período actual"""
        try:
            fecha_inicio = self.start_date_entry.get().strip()
            
            # Obtener fecha fin del campo deshabilitado
            self.end_date_entry.configure(state="normal")
            fecha_fin = self.end_date_entry.get().strip()
            self.end_date_entry.configure(state="disabled")
            
            if not fecha_inicio or not fecha_fin:
                self.period_status_label.configure(
                    text="⚠️ Por favor, complete la fecha de inicio",
                    text_color="#F59E0B"
                )
                return
            
            # Validar formato de fechas
            from datetime import datetime, date
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                fecha_actual = date.today()
            except ValueError:
                self.period_status_label.configure(
                    text="❌ Formato de fecha inválido. Use YYYY-MM-DD",
                    text_color="#EF4444"
                )
                return
            
            # Validaciones
            if fecha_inicio_obj > fecha_fin_obj:
                self.period_status_label.configure(
                    text="❌ La fecha inicio no puede ser posterior a la fecha fin",
                    text_color="#EF4444"
                )
                return
            
            if fecha_fin_obj > fecha_actual:
                # Ajustar fecha fin automáticamente
                fecha_fin = fecha_actual.strftime("%Y-%m-%d")
                fecha_fin_obj = fecha_actual
                self.end_date_entry.configure(state="normal")
                self.end_date_entry.delete(0, "end")
                self.end_date_entry.insert(0, fecha_fin)
                self.end_date_entry.configure(state="disabled")
            
            # Calcular diferencia de días
            dias_diferencia = (fecha_fin_obj - fecha_inicio_obj).days + 1
            
            # Establecer el período
            result = self.set_current_period(fecha_inicio, fecha_fin)
            
            if result:
                period_text = f"✅ Período: {fecha_inicio} a {fecha_fin}"
                if dias_diferencia == 1:
                    period_text += " (1 día)"
                else:
                    period_text += f" ({dias_diferencia} días)"
                
                self.period_status_label.configure(
                    text=period_text,
                    text_color="#16A34A"
                )
                print(f"📅 Usuario seleccionó período: {fecha_inicio} a {fecha_fin}")
            else:
                self.period_status_label.configure(
                    text="❌ Error al aplicar el período",
                    text_color="#EF4444"
                )
                
        except Exception as e:
            print(f"❌ Error aplicando fechas: {str(e)}")
            self.period_status_label.configure(
                text=f"❌ Error: {str(e)}",
                text_color="#EF4444"
            )