"""
Panel de generación de reportes
"""
import customtkinter as ctk
from typing import Dict, Any, Optional


class ReportsPanel(ctk.CTkFrame):
    """Panel para generación de reportes"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="#FFFFFF", 
            corner_radius=15,
            **kwargs
        )
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura el panel de reportes"""
        # Header del panel
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        # Título del panel
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📄 Generar Reportes",
            font=("Arial", 20, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        self.title_label.pack(side="left")
        
        # Estado
        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="⚡ Funcionalidad en desarrollo",
            font=("Arial", 11),
            text_color="#F59E0B"
        )
        self.status_label.pack(side="right")
        
        # Contenido principal
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=12
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Área de opciones de reportes
        self.create_report_options()
    
    def create_report_options(self):
        """Crea las opciones de reportes disponibles"""
        # Frame principal para las opciones
        options_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título de sección
        section_title = ctk.CTkLabel(
            options_frame,
            text="Tipos de Reportes Disponibles",
            font=("Arial", 16, "bold"),
            text_color="#374151"
        )
        section_title.pack(anchor="w", pady=(0, 15))
        
        # Grid de opciones de reportes
        reports_grid = ctk.CTkFrame(options_frame, fg_color="transparent")
        reports_grid.pack(fill="x")
        
        # Configurar grid
        reports_grid.grid_columnconfigure(0, weight=1)
        reports_grid.grid_columnconfigure(1, weight=1)
        
        # Opciones de reportes
        report_options = [
            {
                "title": "📊 Reporte de Ventas",
                "description": "Análisis completo de ventas por período\nIncluye gráficos y métricas detalladas",
                "icon": "📈",
                "color": "#16A34A"
            },
            {
                "title": "🛍️ Reporte de Productos",
                "description": "Análisis de rendimiento de productos\nInventario, ventas y tendencias",
                "icon": "📦",
                "color": "#2563EB"
            },
            {
                "title": "👥 Reporte de Clientes",
                "description": "Análisis del comportamiento de clientes\nSegmentación y patrones de compra",
                "icon": "👤",
                "color": "#7C3AED"
            },
            {
                "title": "💰 Reporte Financiero",
                "description": "Resumen financiero y rentabilidad\nIngresos, costos y márgenes",
                "icon": "💵",
                "color": "#F59E0B"
            }
        ]
        
        # Crear tarjetas de opciones
        for i, option in enumerate(report_options):
            row = i // 2
            col = i % 2
            
            card = self.create_report_card(reports_grid, option)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Separador
        separator = ctk.CTkFrame(options_frame, height=2, fg_color="#E5E7EB")
        separator.pack(fill="x", pady=(20, 15))
        
        # Configuración de exportación
        export_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        export_frame.pack(fill="x")
        
        export_title = ctk.CTkLabel(
            export_frame,
            text="Opciones de Exportación",
            font=("Arial", 14, "bold"),
            text_color="#374151"
        )
        export_title.pack(anchor="w", pady=(0, 10))
        
        # Botones de exportación
        export_buttons_frame = ctk.CTkFrame(export_frame, fg_color="transparent")
        export_buttons_frame.pack(fill="x")
        
        formats = [
            {"name": "PDF", "icon": "📄", "color": "#DC2626"},
            {"name": "Excel", "icon": "📊", "color": "#16A34A"},
            {"name": "CSV", "icon": "📋", "color": "#2563EB"},
            {"name": "PNG", "icon": "🖼️", "color": "#F59E0B"}
        ]
        
        for fmt in formats:
            btn = ctk.CTkButton(
                export_buttons_frame,
                text=f"{fmt['icon']} {fmt['name']}",
                command=lambda f=fmt['name']: self.export_report(f),
                width=100,
                height=35,
                font=("Arial", 11),
                fg_color=fmt['color'],
                hover_color=self._darken_color(fmt['color']),
                corner_radius=6
            )
            btn.pack(side="left", padx=(0, 10))
    
    def create_report_card(self, parent, option):
        """Crea una tarjeta de opción de reporte"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB",
            height=120
        )
        
        # Header de la tarjeta
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        # Icono
        icon_label = ctk.CTkLabel(
            header,
            text=option["icon"],
            font=("Arial", 24)
        )
        icon_label.pack(side="left")
        
        # Título
        title_label = ctk.CTkLabel(
            header,
            text=option["title"],
            font=("Arial", 14, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        title_label.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Descripción
        desc_label = ctk.CTkLabel(
            card,
            text=option["description"],
            font=("Arial", 11),
            text_color="#6B7280",
            anchor="w",
            justify="left"
        )
        desc_label.pack(fill="x", padx=15, pady=(0, 10))
        
        # Botón generar
        generate_btn = ctk.CTkButton(
            card,
            text="Generar Reporte",
            command=lambda: self.generate_report(option["title"]),
            height=30,
            font=("Arial", 11),
            fg_color=option["color"],
            hover_color=self._darken_color(option["color"]),
            corner_radius=6
        )
        generate_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        # Efectos hover
        def on_enter(event):
            card.configure(border_color=option["color"])
        
        def on_leave(event):
            card.configure(border_color="#E5E7EB")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        return card
    
    def generate_report(self, report_type: str):
        """Genera un reporte específico"""
        print(f"🎯 Generando reporte: {report_type}")
        
        # Por ahora mostrar mensaje
        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "Generar Reporte",
            f"Funcionalidad en desarrollo para:\n{report_type}\n\nEsta característica estará disponible próximamente."
        )
    
    def export_report(self, format_type: str):
        """Exporta un reporte en el formato especificado"""
        print(f"💾 Exportando en formato: {format_type}")
        
        # Por ahora mostrar mensaje
        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "Exportar Reporte",
            f"Exportación en formato {format_type}\n\nFuncionalidad en desarrollo."
        )
    
    def _darken_color(self, hex_color: str) -> str:
        """Oscurece un color hex"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darker_rgb = tuple(max(0, c - 30) for c in rgb)
            return '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
        except:
            return "#115E3A"
